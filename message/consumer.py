import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from authentication.models import Dater
from swipe.models import Connection

from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
            return

        self.other_user_id = self.scope["url_route"]["kwargs"]["user_id"]
        self.other_user = await database_sync_to_async(Dater.objects.get)(id=self.other_user_id)

        is_matched = await database_sync_to_async(Connection.matched==True)(self.user, self.other_user)
        if not is_matched:
            await self.close()
            return

        self.room_group_name = f"chat_{min(self.user.id, self.other_user.id)}_{max(self.user.id, self.other_user.id)}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        await database_sync_to_async(Message.objects.create)(
            sender=self.user, receiver=self.other_user, content=message
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": message,
                "sender": self.user.id,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"]
        }))
