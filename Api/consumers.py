import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'chat_room'

        # Join the chat group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Optional: Notify others that a user has joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': 'A new user has joined the chat.',
                'username': 'System',
            }
        )

    async def disconnect(self, close_code):
        # Leave the chat group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Optional: Notify others that a user has left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': 'A user has left the chat.',
                'username': 'System',
            }
        )

    async def receive(self, text_data):
        # Parse incoming message
        data = json.loads(text_data)
        message = data.get('message')

        # Ignore empty or whitespace-only messages
        if not message or not message.strip():
            return

        # Get authenticated user or mark as anonymous
        user = self.scope.get("user")
        is_authenticated = user and user.is_authenticated
        username = user.username if is_authenticated else "Anonymous"

        # Save the message to the database
        await self.save_message(user if is_authenticated else None, message)

        # Broadcast the message to all clients
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    async def chat_message(self, event):
        # Send the message to the WebSocket client
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
        }))

    @database_sync_to_async
    def save_message(self, user, message):
        ChatMessage.objects.create(user=user, message=message)
