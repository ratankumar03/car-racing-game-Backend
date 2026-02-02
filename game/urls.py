from django.urls import path
from .views import (
    GameConfigView, GamePhysicsView,
    CollisionDetectionView, PowerUpView,
    TrackDataView, GameStatsView
)

urlpatterns = [
    # Game configuration
    path('config/', GameConfigView.as_view(), name='game-config'),
    
    # Physics
    path('physics/', GamePhysicsView.as_view(), name='game-physics'),
    
    # Collision detection
    path('collision/', CollisionDetectionView.as_view(), name='collision-detection'),
    
    # Power-ups
    path('powerup/', PowerUpView.as_view(), name='powerup'),
    
    # Track data
    path('track/<int:level_number>/', TrackDataView.as_view(), name='track-data'),
    
    # Statistics
    path('stats/', GameStatsView.as_view(), name='game-stats'),
]
