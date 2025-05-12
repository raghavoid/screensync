import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
import logging
import traceback

logger = logging.getLogger(__name__)

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.room_group_name = f'room_{self.room_id}'
            
            logger.info(f"WebSocket connection attempt to room: {self.room_id}")
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"WebSocket connection accepted for room: {self.room_id}")
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    async def disconnect(self, close_code):
        try:
            logger.info(f"WebSocket disconnected from room: {self.room_id} with code: {close_code}")
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            
            # Notify others that user has left
            if hasattr(self, 'username'):
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'user_leave',
                        'username': self.username
                    }
                )
        except Exception as e:
            logger.error(f"Error in disconnect: {str(e)}")
            logger.error(traceback.format_exc())

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data['type'] == 'message':
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'relay_message',
                        'message': data['message'],
                        'username': self.scope['user'].username,
                    }
                )
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e),
            }))

    async def relay_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
        }))

    async def user_leave(self, event):
        try:
            await self.send(text_data=json.dumps({
                'type': 'leave',
                'username': event['username']
            }))
        except Exception as e:
            logger.error(f"Error in user_leave: {str(e)}")
            logger.error(traceback.format_exc())
