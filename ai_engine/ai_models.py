import numpy as np
import random
from sklearn.linear_model import LinearRegression
import json


class OpponentAI:
    """AI system for controlling opponent cars"""
    
    def __init__(self, difficulty='medium', level=1):
        self.difficulty = difficulty
        self.level = level
        self.base_speed = 100
        self.reaction_time = self._get_reaction_time()
        self.aggression = self._get_aggression()
        self.skill_level = self._get_skill_level()
        
    def _get_reaction_time(self):
        """Get AI reaction time based on difficulty"""
        reaction_times = {
            'easy': 0.8,
            'medium': 0.5,
            'hard': 0.3,
            'expert': 0.15
        }
        return reaction_times.get(self.difficulty, 0.5)
    
    def _get_aggression(self):
        """Get AI aggression level"""
        aggression_levels = {
            'easy': 0.3,
            'medium': 0.5,
            'hard': 0.7,
            'expert': 0.9
        }
        return aggression_levels.get(self.difficulty, 0.5)
    
    def _get_skill_level(self):
        """Get AI skill level multiplier"""
        skill_levels = {
            'easy': 0.7,
            'medium': 0.85,
            'hard': 1.0,
            'expert': 1.2
        }
        return skill_levels.get(self.difficulty, 0.85)
    
    def calculate_speed(self, track_position, obstacles_nearby, player_distance):
        """Calculate AI car speed based on environment"""
        # Base speed calculation
        speed = self.base_speed * self.skill_level
        
        # Adjust for level difficulty
        speed += self.level * 5
        
        # Adjust for obstacles
        if obstacles_nearby:
            speed *= 0.7
        
        # Rubber banding - catch up if behind, slow down if ahead
        if player_distance > 0:  # AI is behind
            speed *= (1 + self.aggression * 0.2)
        elif player_distance < -100:  # AI is far ahead
            speed *= 0.9
        
        # Add some randomness
        speed += random.uniform(-10, 10)
        
        return max(speed, 50)  # Minimum speed
    
    def decide_action(self, game_state):
        """Decide what action AI should take"""
        actions = {
            'accelerate': False,
            'brake': False,
            'turn_left': False,
            'turn_right': False,
            'use_nitro': False
        }
        
        # Check if obstacle ahead
        if game_state.get('obstacle_ahead_distance', float('inf')) < 100:
            if game_state.get('obstacle_left', False):
                actions['turn_right'] = True
            elif game_state.get('obstacle_right', False):
                actions['turn_left'] = True
            else:
                actions['brake'] = True
        else:
            actions['accelerate'] = True
        
        # Use nitro strategically
        if (game_state.get('nitro_available', 0) > 50 and 
            game_state.get('clear_path', True) and
            random.random() < self.aggression):
            actions['use_nitro'] = True
        
        # Add skill-based errors
        if random.random() > self.skill_level:
            # Make a mistake
            if random.random() < 0.5:
                actions['brake'] = True
                actions['accelerate'] = False
        
        return actions
    
    def calculate_path(self, current_position, target_position, obstacles):
        """Calculate optimal path avoiding obstacles"""
        # Simple pathfinding algorithm
        dx = target_position[0] - current_position[0]
        dy = target_position[1] - current_position[1]
        
        # Check if direct path is clear
        path_clear = True
        for obstacle in obstacles:
            if self._intersects_obstacle(current_position, target_position, obstacle):
                path_clear = False
                break
        
        if path_clear:
            return target_position
        
        # Find alternative path
        # Try moving to the side
        alternative_positions = [
            (current_position[0] - 50, current_position[1] + 50),
            (current_position[0] + 50, current_position[1] + 50)
        ]
        
        for pos in alternative_positions:
            clear = True
            for obstacle in obstacles:
                if self._intersects_obstacle(current_position, pos, obstacle):
                    clear = False
                    break
            if clear:
                return pos
        
        return current_position
    
    def _intersects_obstacle(self, start, end, obstacle):
        """Check if path intersects with obstacle"""
        # Simplified collision detection
        obstacle_x, obstacle_y, obstacle_radius = obstacle
        
        # Check if obstacle is on the path
        distance = self._point_to_line_distance(
            obstacle_x, obstacle_y,
            start[0], start[1],
            end[0], end[1]
        )
        
        return distance < obstacle_radius + 20
    
    def _point_to_line_distance(self, px, py, x1, y1, x2, y2):
        """Calculate distance from point to line segment"""
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return np.sqrt((px - x1)**2 + (py - y1)**2)
        
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx**2 + dy**2)))
        
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        return np.sqrt((px - closest_x)**2 + (py - closest_y)**2)


class DifficultyAdjuster:
    """Dynamically adjust game difficulty based on player performance"""
    
    def __init__(self):
        self.performance_history = []
        self.model = LinearRegression()
        self.trained = False
        
    def record_performance(self, performance_data):
        """Record player performance data"""
        self.performance_history.append(performance_data)
        
        # Keep only last 10 performances
        if len(self.performance_history) > 10:
            self.performance_history.pop(0)
    
    def calculate_difficulty(self):
        """Calculate recommended difficulty based on performance"""
        if len(self.performance_history) < 3:
            return 'medium'
        
        # Calculate average performance metrics
        avg_win_rate = np.mean([p.get('won', 0) for p in self.performance_history])
        avg_completion_time = np.mean([p.get('time', 0) for p in self.performance_history])
        avg_collisions = np.mean([p.get('collisions', 0) for p in self.performance_history])
        
        # Decision logic
        if avg_win_rate > 0.8 and avg_collisions < 2:
            return 'hard'
        elif avg_win_rate > 0.6 and avg_collisions < 3:
            return 'medium'
        elif avg_win_rate < 0.4 or avg_collisions > 5:
            return 'easy'
        else:
            return 'medium'
    
    def predict_performance(self, level, car_stats):
        """Predict player performance for a given level and car"""
        if not self.trained and len(self.performance_history) >= 5:
            self._train_model()
        
        if self.trained:
            # Prepare input features
            features = np.array([[
                level,
                car_stats.get('speed', 100),
                car_stats.get('handling', 50),
                car_stats.get('acceleration', 50)
            ]])
            
            # Predict win probability
            win_probability = self.model.predict(features)[0]
            return max(0, min(1, win_probability))
        
        # Default prediction
        return 0.5
    
    def _train_model(self):
        """Train machine learning model on performance history"""
        if len(self.performance_history) < 5:
            return
        
        # Prepare training data
        X = []
        y = []
        
        for perf in self.performance_history:
            features = [
                perf.get('level', 1),
                perf.get('car_speed', 100),
                perf.get('car_handling', 50),
                perf.get('car_acceleration', 50)
            ]
            label = 1 if perf.get('won', False) else 0
            
            X.append(features)
            y.append(label)
        
        X = np.array(X)
        y = np.array(y)
        
        # Train model
        try:
            self.model.fit(X, y)
            self.trained = True
        except Exception as e:
            print(f"Error training model: {e}")
            self.trained = False
    
    def get_recommendations(self, player_stats, car_stats):
        """Get recommendations for player improvement"""
        recommendations = []
        
        if len(self.performance_history) < 2:
            return ["Play more races to get personalized recommendations"]
        
        # Analyze recent performance
        recent_performances = self.performance_history[-5:]
        
        avg_collisions = np.mean([p.get('collisions', 0) for p in recent_performances])
        if avg_collisions > 3:
            recommendations.append("Try to avoid collisions by improving your steering control")
        
        avg_nitro_usage = np.mean([p.get('nitro_used', 0) for p in recent_performances])
        if avg_nitro_usage < 30:
            recommendations.append("Use nitro more strategically to gain speed advantage")
        
        win_rate = np.mean([p.get('won', 0) for p in recent_performances])
        if win_rate < 0.5:
            # Suggest car upgrades
            if car_stats.get('speed', 100) < 150:
                recommendations.append("Upgrade your car's speed for better performance")
            if car_stats.get('handling', 50) < 70:
                recommendations.append("Improve your car's handling for better control")
        
        return recommendations if recommendations else ["Keep up the great work!"]


class TrafficGenerator:
    """Generate realistic traffic patterns"""
    
    def __init__(self, density='medium'):
        self.density = density
        self.traffic_patterns = {
            'low': {'vehicle_count': 5, 'speed_variance': 20},
            'medium': {'vehicle_count': 10, 'speed_variance': 30},
            'high': {'vehicle_count': 15, 'speed_variance': 40}
        }
    
    def generate_traffic(self, track_length, player_position):
        """Generate traffic vehicles"""
        pattern = self.traffic_patterns.get(self.density, self.traffic_patterns['medium'])
        vehicles = []
        
        for i in range(pattern['vehicle_count']):
            position = random.uniform(0, track_length)
            speed = random.uniform(60, 100) + random.uniform(-pattern['speed_variance'], pattern['speed_variance'])
            lane = random.randint(0, 2)  # 3 lanes
            
            vehicle = {
                'id': f'traffic_{i}',
                'position': position,
                'speed': speed,
                'lane': lane,
                'type': random.choice(['car', 'truck', 'bus'])
            }
            vehicles.append(vehicle)
        
        return vehicles
    
    def update_traffic(self, vehicles, delta_time):
        """Update traffic vehicle positions"""
        for vehicle in vehicles:
            vehicle['position'] += vehicle['speed'] * delta_time
            
            # Random lane changes
            if random.random() < 0.01:
                vehicle['lane'] = max(0, min(2, vehicle['lane'] + random.choice([-1, 1])))
        
        return vehicles
