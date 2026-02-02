"""
Django REST API Views for Racing Game
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from .mongodb_models import (
    PlayerDB, CarDB, LevelDB, GameSessionDB, LeaderboardDB
)
from .serializers import (
    PlayerSerializer, CarSerializer, LevelSerializer,
    GameSessionSerializer, LeaderboardSerializer, VoiceCommandSerializer
)
from .voice_agent import voice_agent

# Player Views
class PlayerListCreateView(APIView):
    """List all players or create new player"""
    
    def post(self, request):
        serializer = PlayerSerializer(data=request.data)
        if serializer.is_valid():
            # Check if username exists
            existing = PlayerDB.get_player_by_username(serializer.validated_data['username'])
            if existing:
                return Response(
                    {'error': 'Username already exists'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            player = PlayerDB.create_player(
                username=serializer.validated_data['username'],
                email=serializer.validated_data.get('email', '')
            )
            return Response(PlayerSerializer(player).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PlayerDetailView(APIView):
    """Retrieve, update player"""
    
    def get(self, request, player_id):
        player = PlayerDB.get_player(player_id)
        if player:
            return Response(PlayerSerializer(player).data)
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    def put(self, request, player_id):
        player = PlayerDB.get_player(player_id)
        if not player:
            return Response(
                {'error': 'Player not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        updated_player = PlayerDB.update_player(player_id, request.data)
        return Response(PlayerSerializer(updated_player).data)

class PlayerByUsernameView(APIView):
    """Get player by username"""
    
    def get(self, request, username):
        player = PlayerDB.get_player_by_username(username)
        if player:
            return Response(PlayerSerializer(player).data)
        return Response(
            {'error': 'Player not found'},
            status=status.HTTP_404_NOT_FOUND
        )

# Car Views
class CarListCreateView(APIView):
    """List cars or create new car"""
    
    def get(self, request):
        player_id = request.query_params.get('player_id')
        if player_id:
            cars = CarDB.get_player_cars(player_id)
            return Response(CarSerializer(cars, many=True).data)
        return Response({'error': 'player_id required'}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            car = CarDB.create_car(
                player_id=serializer.validated_data['player_id'],
                car_data=serializer.validated_data
            )
            return Response(CarSerializer(car).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CarDetailView(APIView):
    """Retrieve, update, delete car"""
    
    def get(self, request, car_id):
        car = CarDB.get_car(car_id)
        if car:
            return Response(CarSerializer(car).data)
        return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, car_id):
        car = CarDB.get_car(car_id)
        if not car:
            return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)
        
        updated_car = CarDB.update_car(car_id, request.data)
        return Response(CarSerializer(updated_car).data)

class CarUpgradeView(APIView):
    """Upgrade car attribute"""
    
    def post(self, request, car_id):
        upgrade_type = request.data.get('upgrade_type')
        amount = request.data.get('amount', 10)
        
        if upgrade_type not in ['speed', 'acceleration', 'handling', 'nitro_power']:
            return Response(
                {'error': 'Invalid upgrade type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        car = CarDB.upgrade_car(car_id, upgrade_type, amount)
        if car:
            return Response(CarSerializer(car).data)
        return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)

# Level Views
class LevelListView(APIView):
    """List all levels"""
    
    def get(self, request):
        # Initialize levels if not exists
        LevelDB.initialize_levels()
        levels = LevelDB.get_all_levels()
        return Response(LevelSerializer(levels, many=True).data)

class LevelDetailView(APIView):
    """Get specific level"""
    
    def get(self, request, level_number):
        level = LevelDB.get_level(level_number)
        if level:
            return Response(LevelSerializer(level).data)
        return Response({'error': 'Level not found'}, status=status.HTTP_404_NOT_FOUND)

# Game Session Views
class GameSessionCreateView(APIView):
    """Create new game session"""
    
    def post(self, request):
        player_id = request.data.get('player_id')
        level_number = request.data.get('level_number')
        car_id = request.data.get('car_id')
        
        if not all([player_id, level_number, car_id]):
            return Response(
                {'error': 'player_id, level_number, and car_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session = GameSessionDB.create_session(player_id, level_number, car_id)
        return Response(GameSessionSerializer(session).data, status=status.HTTP_201_CREATED)

class GameSessionDetailView(APIView):
    """Get or update game session"""
    
    def get(self, request, session_id):
        session = GameSessionDB.get_session(session_id)
        if session:
            return Response(GameSessionSerializer(session).data)
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, session_id):
        session = GameSessionDB.update_session(session_id, request.data)
        if session:
            return Response(GameSessionSerializer(session).data)
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

class GameSessionCompleteView(APIView):
    """Complete game session"""
    
    def post(self, request, session_id):
        position = request.data.get('position', 0)
        score = request.data.get('score', 0)
        
        session = GameSessionDB.complete_session(session_id, position, score)
        if session:
            # Update player stats
            won = position == 1
            PlayerDB.update_player_stats(session['player_id'], won)
            
            # Add to leaderboard
            LeaderboardDB.add_score(
                session['player_id'],
                session['level_number'],
                score,
                request.data.get('time', 0)
            )
            
            return Response(GameSessionSerializer(session).data)
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

# Leaderboard Views
class LeaderboardView(APIView):
    """Get leaderboard"""
    
    def get(self, request):
        level_number = request.query_params.get('level_number')
        limit = int(request.query_params.get('limit', 10))
        
        if level_number:
            level_number = int(level_number)
        
        leaderboard = LeaderboardDB.get_leaderboard(level_number, limit)
        return Response(LeaderboardSerializer(leaderboard, many=True).data)

# Voice Agent Views
class VoiceCommandView(APIView):
    """Process voice commands"""
    
    def post(self, request):
        command = request.data.get('command', '')
        context = request.data.get('context', None)
        
        if not command:
            return Response(
                {'error': 'Command required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = voice_agent.process_command(command, context)
        return Response(result)

class VoiceGameTipView(APIView):
    """Get game tip from voice agent"""
    
    def get(self, request):
        level_number = request.query_params.get('level_number')
        if level_number:
            level_number = int(level_number)
        
        result = voice_agent.get_game_tip(level_number)
        return Response(result)

class VoiceFeatureExplainView(APIView):
    """Explain game feature"""
    
    def post(self, request):
        feature_name = request.data.get('feature_name', '')
        
        if not feature_name:
            return Response(
                {'error': 'feature_name required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = voice_agent.explain_feature(feature_name)
        return Response(result)

# Utility Views
@api_view(['GET'])
def health_check(request):
    """API health check"""
    return Response({
        'status': 'healthy',
        'message': 'Racing Game API is running'
    })

@api_view(['POST'])
def initialize_game(request):
    """Initialize game data"""
    LevelDB.initialize_levels()
    return Response({
        'status': 'success',
        'message': 'Game initialized successfully'
    })
