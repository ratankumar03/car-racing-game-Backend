"""
Django REST Framework Serializers for Racing Game
"""
from rest_framework import serializers

class PlayerSerializer(serializers.Serializer):
    """Player Serializer"""
    _id = serializers.CharField(read_only=True)
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField(required=False, allow_blank=True)
    level = serializers.IntegerField(read_only=True)
    coins = serializers.IntegerField(read_only=True)
    experience = serializers.IntegerField(read_only=True)
    total_races = serializers.IntegerField(read_only=True)
    wins = serializers.IntegerField(read_only=True)
    losses = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

class CarCustomizationSerializer(serializers.Serializer):
    """Car Customization Serializer"""
    body_type = serializers.CharField(max_length=50)
    wheels = serializers.CharField(max_length=50)
    spoiler = serializers.CharField(max_length=50)
    paint = serializers.CharField(max_length=50)
    decals = serializers.ListField(child=serializers.CharField(), required=False)

class CarSerializer(serializers.Serializer):
    """Car Serializer"""
    _id = serializers.CharField(read_only=True)
    player_id = serializers.CharField()
    name = serializers.CharField(max_length=100)
    model = serializers.CharField(max_length=50)
    color = serializers.CharField(max_length=20)
    speed = serializers.IntegerField()
    acceleration = serializers.IntegerField()
    handling = serializers.IntegerField()
    nitro_power = serializers.IntegerField()
    customizations = CarCustomizationSerializer()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

class EnvironmentSerializer(serializers.Serializer):
    """Environment Serializer"""
    weather = serializers.CharField()
    time_of_day = serializers.CharField()
    obstacles = serializers.ListField(child=serializers.CharField())

class LevelSerializer(serializers.Serializer):
    """Level Serializer"""
    _id = serializers.CharField(read_only=True)
    level_number = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    difficulty = serializers.CharField(max_length=20)
    track_length = serializers.IntegerField()
    opponents = serializers.IntegerField()
    time_limit = serializers.IntegerField()
    rewards = serializers.DictField()
    environment = EnvironmentSerializer()

class GameSessionSerializer(serializers.Serializer):
    """Game Session Serializer"""
    _id = serializers.CharField(read_only=True)
    player_id = serializers.CharField()
    level_number = serializers.IntegerField()
    car_id = serializers.CharField()
    start_time = serializers.DateTimeField(read_only=True)
    end_time = serializers.DateTimeField(required=False, allow_null=True)
    duration = serializers.IntegerField(required=False)
    position = serializers.IntegerField(required=False)
    score = serializers.IntegerField(required=False)
    collisions = serializers.IntegerField(required=False)
    nitro_used = serializers.IntegerField(required=False)
    status = serializers.CharField(max_length=20)
    completed = serializers.BooleanField()

class LeaderboardSerializer(serializers.Serializer):
    """Leaderboard Serializer"""
    _id = serializers.CharField(read_only=True)
    player_id = serializers.CharField()
    username = serializers.CharField(read_only=True)
    level_number = serializers.IntegerField()
    score = serializers.IntegerField()
    time = serializers.FloatField()
    created_at = serializers.DateTimeField(read_only=True)

class VoiceCommandSerializer(serializers.Serializer):
    """Voice Command Serializer"""
    command = serializers.CharField()
    response = serializers.CharField(read_only=True)
