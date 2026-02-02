"""
Voice Agent Service using OpenRouter API
"""
import requests
from django.conf import settings
import json

class VoiceAgent:
    """Voice Agent for game commands and assistance"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = settings.OPENROUTER_API_URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:3000',
            'X-Title': 'Car Racing Game'
        }
    
    def process_command(self, command, context=None):
        """Process voice command and return response"""
        
        # Build the prompt based on command type
        system_prompt = """You are a helpful AI assistant for a 3D car racing game. 
        You help players with:
        - Game controls and mechanics
        - Car customization advice
        - Racing strategies and tips
        - Level navigation help
        - Understanding game features
        
        Respond in a friendly, concise, and helpful manner. 
        Keep responses short (2-3 sentences) unless detailed explanation is requested."""
        
        user_message = command
        if context:
            user_message = f"Context: {json.dumps(context)}\n\nPlayer Query: {command}"
        
        payload = {
            'model': 'openai/gpt-3.5-turbo',
            'messages': [
                {
                    'role': 'system',
                    'content': system_prompt
                },
                {
                    'role': 'user',
                    'content': user_message
                }
            ],
            'temperature': 0.7,
            'max_tokens': 150
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_message = data['choices'][0]['message']['content']
                return {
                    'success': True,
                    'response': assistant_message,
                    'command': command
                }
            else:
                return {
                    'success': False,
                    'response': 'Sorry, I could not process your command at the moment.',
                    'error': f'API Error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'response': 'Voice agent is temporarily unavailable.',
                'error': str(e)
            }
    
    def get_game_tip(self, level_number=None):
        """Get a racing tip for specific level or general tip"""
        if level_number:
            command = f"Give me a racing tip for level {level_number}"
        else:
            command = "Give me a general racing tip"
        
        return self.process_command(command)
    
    def explain_feature(self, feature_name):
        """Explain a game feature"""
        command = f"Explain the {feature_name} feature in the racing game"
        return self.process_command(command)
    
    def suggest_customization(self, car_stats):
        """Suggest car customization based on current stats"""
        context = {
            'current_stats': car_stats
        }
        command = "What should I upgrade on my car to improve performance?"
        return self.process_command(command, context)

# Global voice agent instance
voice_agent = VoiceAgent()
