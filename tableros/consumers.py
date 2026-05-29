import json
from channels.generic.websocket import AsyncWebsocketConsumer


class TableroConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.tablero_id = self.scope['url_route']['kwargs']['tablero_id']
        self.group_name = f'tablero_{self.tablero_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'tablero_actualizado',
                'data': data
            }
        )

    async def tablero_actualizado(self, event):
        await self.send(text_data=json.dumps(event['data']))