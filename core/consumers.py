from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import AnonymousUser
from urllib.parse import parse_qs
import json

class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "echo_room"
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
        await self.send(text_data="WebSocket connection established.")
    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        print("Received message:", text_data)

        data = json.loads(text_data)
        print("Parsed data:", data)
        wheres = data["to"]
        print("Destination:", wheres)
        msg = data["message"]
        print("Message content:", msg)
        if "user" == wheres:
            await self.channel_layer.group_send(f"user_{data['id']}",{
                "type": "chat",
                "message": msg,
                "Who": self.user.username
            })
        elif "group" == wheres:
            print("Broadcasting to group:", self.room_name)
            await self.channel_layer.group_send(
                self.room_name, 
                {
                    "type": "chat",
                    "message": msg,
                    "Who": self.user.username
                }
            )
    async def chat(self, event):
        message = event["Who"] + ":" + event["message"]
        print("Sending message:", message)
        await self.send(text_data=message)