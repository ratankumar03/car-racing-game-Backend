import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import asyncio


class GameRoomConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time multiplayer racing"""
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'race_{self.room_name}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to race room',
            'room': self.room_name
        }))
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'player_update':
            # Broadcast player position/state to all in room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'player_position',
                    'player_id': data.get('player_id'),
                    'position': data.get('position'),
                    'speed': data.get('speed'),
                    'rotation': data.get('rotation'),
                    'nitro': data.get('nitro'),
                }
            )
        
        elif message_type == 'collision':
            # Broadcast collision event
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'collision_event',
                    'player_id': data.get('player_id'),
                    'collision_type': data.get('collision_type'),
                    'timestamp': data.get('timestamp'),
                }
            )
        
        elif message_type == 'race_start':
            # Broadcast race start
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'race_started',
                    'timestamp': data.get('timestamp'),
                    'countdown': data.get('countdown', 3),
                }
            )
        
        elif message_type == 'race_finish':
            # Broadcast race finish
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'race_finished',
                    'player_id': data.get('player_id'),
                    'time': data.get('time'),
                    'position': data.get('position'),
                }
            )
    
    async def player_position(self, event):
        """Send player position update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'player_update',
            'player_id': event['player_id'],
            'position': event['position'],
            'speed': event['speed'],
            'rotation': event['rotation'],
            'nitro': event['nitro'],
        }))
    
    async def collision_event(self, event):
        """Send collision event to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'collision',
            'player_id': event['player_id'],
            'collision_type': event['collision_type'],
            'timestamp': event['timestamp'],
        }))
    
    async def race_started(self, event):
        """Send race start to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'race_start',
            'timestamp': event['timestamp'],
            'countdown': event['countdown'],
        }))
    
    async def race_finished(self, event):
        """Send race finish to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'race_finish',
            'player_id': event['player_id'],
            'time': event['time'],
            'position': event['position'],
        }))


class GameStateConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for single-player game state updates"""
    
    async def connect(self):
        self.player_id = self.scope['url_route']['kwargs']['player_id']
        self.player_group_name = f'player_{self.player_id}'
        
        # Join player group
        await self.channel_layer.group_add(
            self.player_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to game state',
            'player_id': self.player_id
        }))
    
    async def disconnect(self, close_code):
        # Leave player group
        await self.channel_layer.group_discard(
            self.player_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.dumps(text_data)
        message_type = data.get('type')
        
        if message_type == 'game_state':
            # Send game state update
            await self.send(text_data=json.dumps({
                'type': 'game_state',
                'state': data.get('state'),
                'timestamp': data.get('timestamp'),
            }))
        
        elif message_type == 'ai_update':
            # Send AI opponent updates
            await self.send(text_data=json.dumps({
                'type': 'ai_update',
                'opponents': data.get('opponents'),
                'timestamp': data.get('timestamp'),
            }))
    
    async def game_state_update(self, event):
        """Send game state update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'state': event['state'],
            'timestamp': event['timestamp'],
        }))
    
    async def ai_opponent_update(self, event):
        """Send AI opponent update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'ai_update',
            'opponents': event['opponents'],
            'timestamp': event['timestamp'],
        }))
