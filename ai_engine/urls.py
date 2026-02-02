from django.urls import path
from .views import (
    OpponentAIView, MultipleOpponentsView,
    DifficultyAdjustmentView, TrafficGenerationView,
    TrafficUpdateView, PathfindingView
)

urlpatterns = [
    # AI opponent endpoints
    path('opponent/', OpponentAIView.as_view(), name='opponent-ai'),
    path('opponents/', MultipleOpponentsView.as_view(), name='multiple-opponents'),
    
    # Difficulty adjustment
    path('difficulty/', DifficultyAdjustmentView.as_view(), name='difficulty-adjustment'),
    path('difficulty/<str:player_id>/', DifficultyAdjustmentView.as_view(), name='player-difficulty'),
    
    # Traffic generation
    path('traffic/generate/', TrafficGenerationView.as_view(), name='traffic-generate'),
    path('traffic/update/', TrafficUpdateView.as_view(), name='traffic-update'),
    
    # Pathfinding
    path('pathfinding/', PathfindingView.as_view(), name='pathfinding'),
]
