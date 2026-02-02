from django.urls import path
from .views import (
    VoiceCommandView, ContinuousSpeechView,
    GameStateDescriptionView, TutorialInstructionsView,
    VoiceAssistantView, PerformanceTipsView,
    ActiveCommandsView, CommandMappingsView
)

urlpatterns = [
    # Voice command processing
    path('command/', VoiceCommandView.as_view(), name='voice-command'),
    path('continuous/', ContinuousSpeechView.as_view(), name='continuous-speech'),
    
    # Game state description
    path('describe/', GameStateDescriptionView.as_view(), name='game-state-description'),
    
    # Tutorial
    path('tutorial/<int:level>/', TutorialInstructionsView.as_view(), name='tutorial-instructions'),
    
    # Voice assistant
    path('assistant/', VoiceAssistantView.as_view(), name='voice-assistant'),
    path('assistant/<str:session_id>/', VoiceAssistantView.as_view(), name='voice-assistant-session'),
    
    # Performance tips
    path('tips/', PerformanceTipsView.as_view(), name='performance-tips'),
    
    # Active commands
    path('active/', ActiveCommandsView.as_view(), name='active-commands'),
    
    # Command mappings
    path('mappings/', CommandMappingsView.as_view(), name='command-mappings'),
]
