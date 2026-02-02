from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .ai_models import OpponentAI, DifficultyAdjuster, TrafficGenerator
import json


class OpponentAIView(APIView):
    """API endpoint for opponent AI decisions"""
    
    def post(self, request):
        """Get AI decision for current game state"""
        game_state = request.data
        difficulty = game_state.get('difficulty', 'medium')
        level = game_state.get('level', 1)
        
        # Create AI instance
        ai = OpponentAI(difficulty=difficulty, level=level)
        
        # Calculate AI speed
        speed = ai.calculate_speed(
            track_position=game_state.get('track_position', 0),
            obstacles_nearby=game_state.get('obstacles_nearby', False),
            player_distance=game_state.get('player_distance', 0)
        )
        
        # Decide action
        action = ai.decide_action(game_state)
        
        return Response({
            'speed': speed,
            'action': action,
            'reaction_time': ai.reaction_time,
            'aggression': ai.aggression,
            'skill_level': ai.skill_level
        })


class MultipleOpponentsView(APIView):
    """API endpoint for multiple opponent AI decisions"""
    
    def post(self, request):
        """Get AI decisions for multiple opponents"""
        game_state = request.data
        opponent_count = game_state.get('opponent_count', 3)
        difficulty = game_state.get('difficulty', 'medium')
        level = game_state.get('level', 1)
        
        opponents = []
        
        for i in range(opponent_count):
            # Vary difficulty for each opponent
            varied_difficulty = difficulty
            if difficulty == 'medium':
                varied_difficulty = ['easy', 'medium', 'hard'][i % 3]
            
            ai = OpponentAI(difficulty=varied_difficulty, level=level)
            
            # Calculate position offset for each opponent
            position_offset = i * 50
            
            speed = ai.calculate_speed(
                track_position=game_state.get('track_position', 0) + position_offset,
                obstacles_nearby=game_state.get('obstacles_nearby', False),
                player_distance=game_state.get('player_distance', 0) - position_offset
            )
            
            action = ai.decide_action(game_state)
            
            opponents.append({
                'id': f'opponent_{i}',
                'speed': speed,
                'action': action,
                'difficulty': varied_difficulty,
                'position_offset': position_offset
            })
        
        return Response({'opponents': opponents})


class DifficultyAdjustmentView(APIView):
    """API endpoint for dynamic difficulty adjustment"""
    
    adjusters = {}  # Store adjusters per player
    
    def post(self, request):
        """Record performance and get difficulty recommendation"""
        player_id = request.data.get('player_id')
        performance_data = request.data.get('performance_data')
        
        if not player_id or not performance_data:
            return Response({
                'error': 'player_id and performance_data required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create difficulty adjuster for player
        if player_id not in self.adjusters:
            self.adjusters[player_id] = DifficultyAdjuster()
        
        adjuster = self.adjusters[player_id]
        
        # Record performance
        adjuster.record_performance(performance_data)
        
        # Calculate recommended difficulty
        recommended_difficulty = adjuster.calculate_difficulty()
        
        # Get car stats for predictions
        car_stats = request.data.get('car_stats', {})
        level = request.data.get('level', 1)
        
        # Predict performance
        win_probability = adjuster.predict_performance(level, car_stats)
        
        # Get recommendations
        player_stats = request.data.get('player_stats', {})
        recommendations = adjuster.get_recommendations(player_stats, car_stats)
        
        return Response({
            'recommended_difficulty': recommended_difficulty,
            'win_probability': win_probability,
            'recommendations': recommendations,
            'performance_history_count': len(adjuster.performance_history)
        })
    
    def get(self, request, player_id):
        """Get current difficulty recommendation for player"""
        if player_id not in self.adjusters:
            return Response({
                'recommended_difficulty': 'medium',
                'message': 'No performance history yet'
            })
        
        adjuster = self.adjusters[player_id]
        recommended_difficulty = adjuster.calculate_difficulty()
        
        return Response({
            'recommended_difficulty': recommended_difficulty,
            'performance_history_count': len(adjuster.performance_history)
        })


class TrafficGenerationView(APIView):
    """API endpoint for traffic generation"""
    
    def post(self, request):
        """Generate traffic for the track"""
        density = request.data.get('density', 'medium')
        track_length = request.data.get('track_length', 5000)
        player_position = request.data.get('player_position', 0)
        
        generator = TrafficGenerator(density=density)
        vehicles = generator.generate_traffic(track_length, player_position)
        
        return Response({
            'vehicles': vehicles,
            'count': len(vehicles),
            'density': density
        })


class TrafficUpdateView(APIView):
    """API endpoint for updating traffic"""
    
    def post(self, request):
        """Update traffic vehicle positions"""
        vehicles = request.data.get('vehicles', [])
        delta_time = request.data.get('delta_time', 0.016)  # ~60 FPS
        density = request.data.get('density', 'medium')
        
        generator = TrafficGenerator(density=density)
        updated_vehicles = generator.update_traffic(vehicles, delta_time)
        
        return Response({
            'vehicles': updated_vehicles,
            'count': len(updated_vehicles)
        })


class PathfindingView(APIView):
    """API endpoint for AI pathfinding"""
    
    def post(self, request):
        """Calculate optimal path for AI"""
        difficulty = request.data.get('difficulty', 'medium')
        level = request.data.get('level', 1)
        current_position = request.data.get('current_position', [0, 0])
        target_position = request.data.get('target_position', [100, 100])
        obstacles = request.data.get('obstacles', [])
        
        ai = OpponentAI(difficulty=difficulty, level=level)
        optimal_path = ai.calculate_path(
            current_position,
            target_position,
            obstacles
        )
        
        return Response({
            'optimal_path': optimal_path,
            'current_position': current_position,
            'target_position': target_position
        })
