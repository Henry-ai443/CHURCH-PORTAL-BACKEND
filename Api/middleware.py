# middleware.py

from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware

@database_sync_to_async
def get_user_from_token(token_key):
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope['query_string'].decode()
        params = parse_qs(query_string)
        token_key = params.get('token')
        if token_key:
            user = await get_user_from_token(token_key[0])
            scope['user'] = user
        else:
            scope['user'] = AnonymousUser()
        return await super().__call__(scope, receive, send)
