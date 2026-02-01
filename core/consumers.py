from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from .models import User,Messages
import json

ONLINE_USER = list()

@database_sync_to_async
def save_message(sender, receiver_id, content):
    receiver = User.objects.get(id=receiver_id)
    return Messages.objects.create(
        sender=sender,
        receiver=receiver,
        content=content
    )


@database_sync_to_async
def get_unread_messages(user):
    return list(
        Messages.objects
        .filter(receiver=user, is_read=False)
        .values(
            "id",
            "sender__id",
            "sender__username",
            "content",
        )
        .order_by("timestamp")
    )

@database_sync_to_async
def mark_as_read(msg_id):
    Messages.objects.filter(id=msg_id).update(is_read=True)

@database_sync_to_async
def delete_message(msg_id: int) -> None:
    Messages.objects.filter(id=msg_id).delete()


class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "Global"
        self.user = AnonymousUser()
        query_string = self.scope["query_string"].decode()
        token_key = parse_qs(query_string).get("token", [None])[0]
        if not token_key:
            await self.close()
            return
        try:
            token = await Token.objects.select_related("user").aget(key=token_key)
            self.user = token.user
        except Token.DoesNotExist:
            await self.close()
            return
        await self.accept()
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.channel_layer.group_add(
            f"user_{self.user.id}",
            self.channel_name
        )
        ONLINE_USER.append(self.user.id)
        unread = await get_unread_messages(self.user)
        for msg in unread:
            await self.send(text_data=json.dumps({
                "from": "user",
                "id": msg["sender__id"],
                "who": msg["sender__username"],
                "message": msg["content"],
            }))
            await mark_as_read(msg["id"])
            #await delete_message(msg["id"])
            
        await self.send(text_data='{"message":"Connected to WebSocket","from":"system","who":"server"}')
    async def disconnect(self, close_code):
        ONLINE_USER.remove(self.user.id)
        pass
    async def receive(self, text_data):
        data = json.loads(text_data)
        wheres = data["to"]
        msg = data["message"]
        if "user" == wheres:
            message_obj = await save_message(self.user, data['id'], msg)
            if data["id"] in ONLINE_USER:
                await mark_as_read(message_obj.id)
                #await delete_message(msg["id"])
            await self.channel_layer.group_send(f"user_{data['id']}",{
                "type": "chat",
                "message": msg,
                "to":"user",
                "Who": self.user.username,
                "fn": self.user.first_name,
                "ln": self.user.last_name,
                "Id":self.user.id
            })
        elif "global" == wheres:
            await self.channel_layer.group_send(
                self.room_name, 
                {
                    "type": "chat",
                    "to":"global",
                    "message": msg,
                    "Who": self.user.username,
                    "fn": self.user.first_name,
                    "ln": self.user.last_name,
                    "Id":self.user.id
                }
            )

    async def chat(self, event):
        payload = {
            "from": event.get("to"),
            "id": event.get("Id"),
            "who": event.get("Who"),
            "First_name": event.get("fn", ""),   # ALWAYS present
            "Last_name": event.get("ln", ""),    # ALWAYS present
            "message": event.get("message"),
        }

        await self.send(text_data=json.dumps(payload))
