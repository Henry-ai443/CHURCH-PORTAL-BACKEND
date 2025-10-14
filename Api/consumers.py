import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    # NOTE: Class-level set is per-process only. For multi-process/global tracking,
    # use a shared store like Redis or cache.
    online_users = set()

    async def connect(self):
        self.room_group_name = 'chat_room'
        self.user = self.scope.get("user")

        # Join the chat group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Add user to online users and notify others
        if self.user and self.user.is_authenticated:
            self.online_users.add(self.user.username)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'online_status',
                    'username': self.user.username,
                    'status': 'online',
                }
            )

    async def disconnect(self, close_code):
        # Leave the chat group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Remove user from online users and notify others
        if self.user and self.user.is_authenticated and self.user.username in self.online_users:
            self.online_users.remove(self.user.username)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'online_status',
                    'username': self.user.username,
                    'status': 'offline',
                }
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'chat_message':
            message = data.get('message')
            if not message or not message.strip():
                return

            username = self.user.username if (self.user and self.user.is_authenticated) else "Anonymous"
            await self.save_message(self.user if self.user and self.user.is_authenticated else None, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                }
            )

        elif message_type == 'typing':
            username = self.user.username if (self.user and self.user.is_authenticated) else "Anonymous"
            is_typing = data.get('is_typing', False)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing',
                    'username': username,
                    'is_typing': is_typing,
                }
            )

        elif message_type == 'read':
            message_id = data.get('message_id')
            if message_id:
                await self.mark_message_read(message_id, self.user)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'read_receipt',
                        'username': self.user.username if self.user else 'Anonymous',
                        'message_id': message_id,
                    }
                )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username'],
        }))

    async def typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': event['username'],
            'is_typing': event['is_typing'],
        }))

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read',
            'username': event['username'],
            'message_id': event['message_id'],
        }))

    async def online_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'online_status',
            'username': event['username'],
            'status': event['status'],  # 'online' or 'offline'
        }))

    @database_sync_to_async
    def save_message(self, user, message):
        try:
            return ChatMessage.objects.create(user=user, message=message)
        except Exception as e:
            logger.error(f"Failed to save message: {e}")

    @database_sync_to_async
    def mark_message_read(self, message_id, user):
        try:
            msg = ChatMessage.objects.get(id=message_id)
            if user and user.is_authenticated:
                msg.read_by.add(user)
                msg.save()
        except ChatMessage.DoesNotExist:
            logger.warning(f"Message with id {message_id} does not exist.")
        except Exception as e:
            logger.error(f"Error marking message read: {e}")
