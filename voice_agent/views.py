from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .voice_processor import VoiceCommandProcessor, VoiceAssistant, SpeechToGameAction


class VoiceCommandView(APIView):
    """API endpoint for processing voice commands"""
    
    processor = VoiceCommandProcessor()
    
    def post(self, request):
        """Process a voice command"""
        text_input = request.data.get('text')
        
        if not text_input:
            return Response({
                'error': 'text parameter required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        result = self.processor.process_voice_command(text_input)
        
        return Response(result)


class ContinuousSpeechView(APIView):
    """API endpoint for continuous speech processing"""
    
    speech_processor = SpeechToGameAction()
    
    def post(self, request):
        """Process continuous speech with multiple commands"""
        speech_text = request.data.get('text')
        
        if not speech_text:
            return Response({
                'error': 'text parameter required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        commands = self.speech_processor.process_continuous_speech(speech_text)
        
        return Response({
            'commands': commands,
            'count': len(commands)
        })


class GameStateDescriptionView(APIView):
    """API endpoint for generating game state descriptions"""
    
    processor = VoiceCommandProcessor()
    
    def post(self, request):
        """Generate natural language description of game state"""
        game_state = request.data
        
        description = self.processor.get_game_state_description(game_state)
        
        return Response({
            'description': description,
            'game_state': game_state
        })


class TutorialInstructionsView(APIView):
    """API endpoint for generating tutorial instructions"""
    
    processor = VoiceCommandProcessor()
    
    def get(self, request, level):
        """Get tutorial instructions for a level"""
        instructions = self.processor.generate_tutorial_instructions(level)
        
        return Response({
            'level': level,
            'instructions': instructions
        })


class VoiceAssistantView(APIView):
    """API endpoint for voice assistant chat"""
    
    assistants = {}  # Store assistants per session
    
    def post(self, request):
        """Chat with voice assistant"""
        session_id = request.data.get('session_id', 'default')
        user_message = request.data.get('message')
        game_context = request.data.get('game_context')
        
        if not user_message:
            return Response({
                'error': 'message parameter required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create assistant for session
        if session_id not in self.assistants:
            self.assistants[session_id] = VoiceAssistant()
        
        assistant = self.assistants[session_id]
        
        # Get response
        response_message = assistant.chat(user_message, game_context)
        
        return Response({
            'message': response_message,
            'session_id': session_id
        })
    
    def delete(self, request, session_id):
        """Reset assistant conversation"""
        if session_id in self.assistants:
            self.assistants[session_id].reset_conversation()
            return Response({
                'message': 'Conversation reset',
                'session_id': session_id
            })
        return Response({
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)


class PerformanceTipsView(APIView):
    """API endpoint for performance tips"""
    
    assistant = VoiceAssistant()
    
    def post(self, request):
        """Get personalized tips based on performance"""
        player_performance = request.data
        
        tips = self.assistant.provide_tips(player_performance)
        
        return Response({
            'tips': tips,
            'performance': player_performance
        })


class ActiveCommandsView(APIView):
    """API endpoint for managing active commands"""
    
    speech_processor = SpeechToGameAction()
    
    def get(self, request):
        """Get currently active commands"""
        active_commands = self.speech_processor.get_active_commands()
        
        return Response({
            'active_commands': active_commands,
            'count': len(active_commands)
        })
    
    def post(self, request):
        """Activate a command"""
        command = request.data.get('command')
        
        if not command:
            return Response({
                'error': 'command parameter required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.speech_processor.activate_command(command)
        
        return Response({
            'message': 'Command activated',
            'command': command,
            'active_commands': self.speech_processor.get_active_commands()
        })
    
    def delete(self, request):
        """Clear all active commands"""
        command = request.data.get('command')
        
        if command:
            self.speech_processor.deactivate_command(command)
            message = f'Command {command} deactivated'
        else:
            self.speech_processor.clear_commands()
            message = 'All commands cleared'
        
        return Response({
            'message': message,
            'active_commands': self.speech_processor.get_active_commands()
        })


class CommandMappingsView(APIView):
    """API endpoint for getting available voice commands"""
    
    processor = VoiceCommandProcessor()
    
    def get(self, request):
        """Get all available voice command mappings"""
        return Response({
            'commands': self.processor.command_mappings,
            'count': len(self.processor.command_mappings)
        })
