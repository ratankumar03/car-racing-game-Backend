"""
URL Configuration for Racing API
"""
from django.urls import path
from . import views

urlpatterns = [
    # Utility
    path('health/', views.health_check, name='health_check'),
    path('initialize/', views.initialize_game, name='initialize_game'),
    
    # Players
    path('players/', views.PlayerListCreateView.as_view(), name='player_list_create'),
    path('players/username/<str:username>/', views.PlayerByUsernameView.as_view(), name='player_by_username'),
    path('players/<str:player_id>/', views.PlayerDetailView.as_view(), name='player_detail'),
    
    # Cars
    path('cars/', views.CarListCreateView.as_view(), name='car_list_create'),
    path('cars/<str:car_id>/', views.CarDetailView.as_view(), name='car_detail'),
    path('cars/<str:car_id>/upgrade/', views.CarUpgradeView.as_view(), name='car_upgrade'),
    
    # Levels
    path('levels/', views.LevelListView.as_view(), name='level_list'),
    path('levels/<int:level_number>/', views.LevelDetailView.as_view(), name='level_detail'),
    
    # Game Sessions
    path('sessions/', views.GameSessionCreateView.as_view(), name='session_create'),
    path('sessions/<str:session_id>/', views.GameSessionDetailView.as_view(), name='session_detail'),
    path('sessions/<str:session_id>/complete/', views.GameSessionCompleteView.as_view(), name='session_complete'),
    
    # Leaderboard
    path('leaderboard/', views.LeaderboardView.as_view(), name='leaderboard'),
    
    # Voice Agent
    path('voice/command/', views.VoiceCommandView.as_view(), name='voice_command'),
    path('voice/tip/', views.VoiceGameTipView.as_view(), name='voice_tip'),
    path('voice/explain/', views.VoiceFeatureExplainView.as_view(), name='voice_explain'),
]
