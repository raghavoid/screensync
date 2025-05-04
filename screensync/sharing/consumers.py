import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Room

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']
        
        if message_type == 'offer':
            # Forward offer to target user
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_offer',
                    'offer': data['offer'],
                    'username': data['username'],
                    'target': data['target']
                }
            )
        
        elif message_type == 'answer':
            # Forward answer to target user
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_answer',
                    'answer': data['answer'],
                    'username': data['username'],
                    'target': data['target']
                }
            )
        
        elif message_type == 'candidate':
            # Forward ICE candidate to target user
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_candidate',
                    'candidate': data['candidate'],
                    'username': data['username'],
                    'target': data['target']
                }
            )
    
    # Handler for WebRTC offer
    async def webrtc_offer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'offer',
            'offer': event['offer'],
            'username': event['username'],
            'target': event['target']
        }))
    
    # Handler for WebRTC answer
    async def webrtc_answer(self, event):
        await self.send(text_data=json.dumps({
            'type': 'answer',
            'answer': event['answer'],
            'username': event['username'],
            'target': event['target']
        }))
    
    # Handler for WebRTC ICE candidate
    async def webrtc_candidate(self, event):
        await self.send(text_data=json.dumps({
            'type': 'candidate',
            'candidate': event['candidate'],
            'username': event['username'],
            'target': event['target']
        }))
    
    @database_sync_to_async
    def get_username(self, user_id):
        try:
            return User.objects.get(id=user_id).username
        except User.DoesNotExist:
            return "Unknown User"