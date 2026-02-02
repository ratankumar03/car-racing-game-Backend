import requests
import json
from django.conf import settings


class VoiceCommandProcessor:
    """Process voice commands using OpenRouter API"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = settings.OPENROUTER_API_URL
        self.command_mappings = {
            'accelerate': ['accelerate', 'speed up', 'go faster', 'gas', 'forward'],
            'brake': ['brake', 'slow down', 'stop', 'slow'],
            'turn_left': ['turn left', 'go left', 'left turn', 'steer left'],
            'turn_right': ['turn right', 'go right', 'right turn', 'steer right'],
            'nitro': ['nitro', 'boost', 'turbo', 'use nitro', 'activate boost'],
            'pause': ['pause', 'stop game', 'hold on'],
            'resume': ['resume', 'continue', 'start again'],
            'restart': ['restart', 'start over', 'new race'],
        }
    
    def process_voice_command(self, text_input):
        """Process voice command text and return game action"""
        # Normalize input
        text_input = text_input.lower().strip()
        
        # Direct command matching
        for action, keywords in self.command_mappings.items():
            for keyword in keywords:
                if keyword in text_input:
                    return {
                        'action': action,
                        'confidence': 0.95,
                        'original_text': text_input
                    }
        
        # Use OpenRouter API for more complex understanding
        try:
            action = self._process_with_ai(text_input)
            return {
                'action': action,
                'confidence': 0.8,
                'original_text': text_input
            }
        except Exception as e:
            return {
                'action': 'unknown',
                'confidence': 0.0,
                'original_text': text_input,
                'error': str(e)
            }
    
    def _process_with_ai(self, text_input):
        """Use OpenRouter API to understand complex commands"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        prompt = f"""You are a voice command interpreter for a car racing game. 
The user said: "{text_input}"

Available actions are:
- accelerate: speed up the car
- brake: slow down or stop
- turn_left: turn the car left
- turn_right: turn the car right
- nitro: activate nitro boost
- pause: pause the game
- resume: resume the game
- restart: restart the race
- unknown: command not recognized

Return ONLY the action name as a single word, nothing else."""

        payload = {
            'model': 'anthropic/claude-3-haiku',
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 50
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                action = data['choices'][0]['message']['content'].strip().lower()
                
                # Validate action
                valid_actions = ['accelerate', 'brake', 'turn_left', 'turn_right', 
                               'nitro', 'pause', 'resume', 'restart', 'unknown']
                
                if action in valid_actions:
                    return action
                else:
                    return 'unknown'
            else:
                return 'unknown'
        except Exception as e:
            print(f"OpenRouter API Error: {e}")
            return 'unknown'
    
    def get_game_state_description(self, game_state):
        """Convert game state to natural language description"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        prompt = f"""Describe this racing game state in a short, exciting sentence:
Speed: {game_state.get('speed', 0)} km/h
Position: {game_state.get('position', 'Unknown')}
Level: {game_state.get('level', 1)}
Nitro: {game_state.get('nitro', 0)}%
Distance: {game_state.get('distance', 0)}m

Make it sound exciting like a race commentator!"""

        payload = {
            'model': 'anthropic/claude-3-haiku',
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 100
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                description = data['choices'][0]['message']['content'].strip()
                return description
            else:
                return f"Racing at {game_state.get('speed', 0)} km/h!"
        except Exception as e:
            print(f"OpenRouter API Error: {e}")
            return f"Racing at {game_state.get('speed', 0)} km/h!"
    
    def generate_tutorial_instructions(self, level):
        """Generate contextual tutorial instructions"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        prompt = f"""Generate brief tutorial instructions for level {level} of a car racing game.
Keep it under 3 sentences and make it helpful for the player.
Focus on what they should know for this level."""

        payload = {
            'model': 'anthropic/claude-3-haiku',
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 150
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                instructions = data['choices'][0]['message']['content'].strip()
                return instructions
            else:
                return "Control your car with arrow keys and use nitro for extra speed!"
        except Exception as e:
            print(f"OpenRouter API Error: {e}")
            return "Control your car with arrow keys and use nitro for extra speed!"


class VoiceAssistant:
    """AI voice assistant for gameplay guidance"""
    
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.api_url = settings.OPENROUTER_API_URL
        self.conversation_history = []
    
    def chat(self, user_message, game_context=None):
        """Have a conversation with the player"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        # Build context
        context = "You are a helpful racing game assistant. "
        if game_context:
            context += f"Current game state: {json.dumps(game_context)}. "
        
        context += "Provide brief, encouraging responses to help the player."
        
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        
        # Prepare messages
        messages = [
            {'role': 'system', 'content': context}
        ] + self.conversation_history[-5:]  # Keep last 5 messages
        
        payload = {
            'model': 'anthropic/claude-3-haiku',
            'messages': messages,
            'max_tokens': 200
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_message = data['choices'][0]['message']['content'].strip()
                
                # Add to history
                self.conversation_history.append({
                    'role': 'assistant',
                    'content': assistant_message
                })
                
                return assistant_message
            else:
                return "I'm here to help! Keep racing and you'll do great!"
        except Exception as e:
            print(f"OpenRouter API Error: {e}")
            return "I'm here to help! Keep racing and you'll do great!"
    
    def provide_tips(self, player_performance):
        """Provide personalized tips based on performance"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        prompt = f"""Based on this racing performance, give 2-3 brief tips:
Win rate: {player_performance.get('win_rate', 0)}%
Average collisions: {player_performance.get('avg_collisions', 0)}
Average speed: {player_performance.get('avg_speed', 0)} km/h

Be encouraging and specific!"""

        payload = {
            'model': 'anthropic/claude-3-haiku',
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 200
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                tips = data['choices'][0]['message']['content'].strip()
                return tips
            else:
                return "Keep practicing! Focus on smooth steering and timing your nitro boosts."
        except Exception as e:
            print(f"OpenRouter API Error: {e}")
            return "Keep practicing! Focus on smooth steering and timing your nitro boosts."
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []


class SpeechToGameAction:
    """Convert speech patterns to game actions"""
    
    def __init__(self):
        self.command_processor = VoiceCommandProcessor()
        self.active_commands = set()
    
    def process_continuous_speech(self, speech_text):
        """Process continuous speech for multiple commands"""
        # Split by common separators
        commands = []
        
        # Process each part
        parts = speech_text.lower().split(' and ')
        for part in parts:
            part = part.split(' then ')
            for subpart in part:
                result = self.command_processor.process_voice_command(subpart.strip())
                if result['action'] != 'unknown':
                    commands.append(result)
        
        return commands
    
    def activate_command(self, command):
        """Activate a command (for hold actions)"""
        self.active_commands.add(command)
    
    def deactivate_command(self, command):
        """Deactivate a command"""
        self.active_commands.discard(command)
    
    def get_active_commands(self):
        """Get currently active commands"""
        return list(self.active_commands)
    
    def clear_commands(self):
        """Clear all active commands"""
        self.active_commands.clear()
