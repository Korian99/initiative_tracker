from channels.generic.websocket import AsyncWebsocketConsumer
import json

class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.lobby_id = str(self.scope['url_route']['kwargs']['lobby_id'])
        await self.channel_layer.group_add(self.lobby_id, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.lobby_id, self.channel_name)

    async def receive(self, text_data):
        # Optional: handle manual refresh triggers from client
        data = json.loads(text_data)
        if data.get("action") == "refresh":
            await self.broadcast_refresh_signal()

    async def send_update(self, event):
        """
        Receives messages from the group layer and tells HTMX to refresh
        """
        await self.send(text_data=json.dumps({"action": "refresh"}))

    async def broadcast_refresh_signal(self):
        """
        Tell everyone in this lobby to refresh their HTMX content
        """
        await self.channel_layer.group_send(
            self.lobby_id,
            {
                "type": "send_update",
                "message": {}  # no HTML needed, just a signal
            }
        )
