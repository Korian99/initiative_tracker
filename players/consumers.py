import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Access the lobby_code from the scope:
        self.lobby_code = self.scope["url_route"]["kwargs"]["lobby_code"]
        self.group_name = f"lobby_{self.lobby_code}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
    
    async def character_update(self, event):
        await self.send(text_data=json.dumps({
            "hx-trigger": "character_update"
        }))
