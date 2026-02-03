"""
MongoDB Database Operations for Racing Game
"""
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from django.conf import settings
from datetime import datetime
from bson import ObjectId
import copy

class _InsertResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id

class _QueryResult:
    def __init__(self, items):
        self._items = items

    def sort(self, key, direction):
        reverse = direction == -1
        self._items.sort(key=lambda item: item.get(key), reverse=reverse)
        return self

    def limit(self, count):
        self._items = self._items[:count]
        return self

    def __iter__(self):
        return iter(self._items)

class _InMemoryCollection:
    def __init__(self):
        self._items = []

    def insert_one(self, doc):
        new_doc = copy.deepcopy(doc)
        if '_id' not in new_doc:
            new_doc['_id'] = ObjectId()
        self._items.append(new_doc)
        return _InsertResult(new_doc['_id'])

    def find_one(self, filter=None):
        filter = filter or {}
        for item in self._items:
            if _matches_filter(item, filter):
                return copy.deepcopy(item)
        return None

    def find(self, filter=None):
        filter = filter or {}
        items = [copy.deepcopy(item) for item in self._items if _matches_filter(item, filter)]
        return _QueryResult(items)

    def update_one(self, filter, update):
        for idx, item in enumerate(self._items):
            if _matches_filter(item, filter):
                if '$set' in update:
                    for key, value in update['$set'].items():
                        item[key] = value
                if '$inc' in update:
                    for key, value in update['$inc'].items():
                        item[key] = item.get(key, 0) + value
                self._items[idx] = item
                return

def _matches_filter(item, filter):
    for key, expected in filter.items():
        if key not in item or item[key] != expected:
            return False
    return True

def _safe_object_id(value):
    try:
        return ObjectId(str(value))
    except Exception:
        return None

class MongoDB:
    """MongoDB Connection and Operations"""

    def __init__(self):
        # Use MongoDB Atlas URI if available, otherwise use local connection.
        # Fall back to in-memory collections if connection fails.
        mongodb_uri = settings.MONGODB_SETTINGS.get('uri')
        self.client = None
        self.db = None
        try:
            if mongodb_uri:
                # Production: MongoDB Atlas
                self.client = MongoClient(
                    mongodb_uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                    socketTimeoutMS=5000,
                )
            else:
                # Development: Local MongoDB
                self.client = MongoClient(
                    settings.MONGODB_SETTINGS['host'],
                    settings.MONGODB_SETTINGS['port'],
                    serverSelectionTimeoutMS=3000,
                    connectTimeoutMS=3000,
                    socketTimeoutMS=3000,
                )
            self.client.admin.command('ping')
            self.db = self.client[settings.MONGODB_SETTINGS['db']]
        except PyMongoError:
            self.client = None
            self.db = None

        # Collections
        if self.db is not None:
            self.players = self.db['players']
            self.cars = self.db['cars']
            self.levels = self.db['levels']
            self.game_sessions = self.db['game_sessions']
            self.leaderboard = self.db['leaderboard']
            self.car_customizations = self.db['car_customizations']
        else:
            self.players = _InMemoryCollection()
            self.cars = _InMemoryCollection()
            self.levels = _InMemoryCollection()
            self.game_sessions = _InMemoryCollection()
            self.leaderboard = _InMemoryCollection()
            self.car_customizations = _InMemoryCollection()

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

# Global MongoDB instance
mongo_db = MongoDB()

class PlayerDB:
    """Player Database Operations"""

    @staticmethod
    def create_player(username, email):
        """Create a new player"""
        player = {
            'username': username,
            'email': email,
            'level': 1,
            'coins': 1000,
            'experience': 0,
            'total_races': 0,
            'wins': 0,
            'losses': 0,
            'created_at': datetime.now(),
            'last_login': datetime.now()
        }
        result = mongo_db.players.insert_one(player)
        player['_id'] = str(result.inserted_id)
        return player

    @staticmethod
    def get_player(player_id):
        """Get player by ID"""
        oid = _safe_object_id(player_id)
        player = mongo_db.players.find_one({'_id': oid if oid else player_id})
        if player:
            player['_id'] = str(player['_id'])
        return player

    @staticmethod
    def get_player_by_username(username):
        """Get player by username"""
        player = mongo_db.players.find_one({'username': username})
        if player:
            player['_id'] = str(player['_id'])
        return player

    @staticmethod
    def update_player(player_id, update_data):
        """Update player data"""
        oid = _safe_object_id(player_id)
        mongo_db.players.update_one(
            {'_id': oid if oid else player_id},
            {'$set': update_data}
        )
        return PlayerDB.get_player(player_id)

    @staticmethod
    def update_player_stats(player_id, won=False):
        """Update player statistics after race"""
        oid = _safe_object_id(player_id)
        update = {
            '$inc': {
                'total_races': 1,
                'wins' if won else 'losses': 1,
                'experience': 50 if won else 10,
                'coins': 100 if won else 20
            }
        }
        mongo_db.players.update_one({'_id': oid if oid else player_id}, update)
        return PlayerDB.get_player(player_id)

class CarDB:
    """Car Database Operations"""

    @staticmethod
    def create_car(player_id, car_data):
        """Create a new car for player"""
        car = {
            'player_id': player_id,
            'name': car_data.get('name', 'My Car'),
            'model': car_data.get('model', 'default'),
            'color': car_data.get('color', '#FF0000'),
            'speed': car_data.get('speed', 100),
            'acceleration': car_data.get('acceleration', 100),
            'handling': car_data.get('handling', 100),
            'nitro_power': car_data.get('nitro_power', 100),
            'customizations': {
                'body_type': car_data.get('body_type', 'sport'),
                'wheels': car_data.get('wheels', 'default'),
                'spoiler': car_data.get('spoiler', 'none'),
                'paint': car_data.get('paint', 'glossy'),
                'decals': car_data.get('decals', [])
            },
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        result = mongo_db.cars.insert_one(car)
        car['_id'] = str(result.inserted_id)
        return car

    @staticmethod
    def get_car(car_id):
        """Get car by ID"""
        oid = _safe_object_id(car_id)
        car = mongo_db.cars.find_one({'_id': oid if oid else car_id})
        if car:
            car['_id'] = str(car['_id'])
        return car

    @staticmethod
    def get_player_cars(player_id):
        """Get all cars owned by player"""
        cars = list(mongo_db.cars.find({'player_id': player_id}))
        for car in cars:
            car['_id'] = str(car['_id'])
        return cars

    @staticmethod
    def update_car(car_id, update_data):
        """Update car specifications"""
        oid = _safe_object_id(car_id)
        update_data['updated_at'] = datetime.now()
        mongo_db.cars.update_one(
            {'_id': oid if oid else car_id},
            {'$set': update_data}
        )
        return CarDB.get_car(car_id)

    @staticmethod
    def upgrade_car(car_id, upgrade_type, amount):
        """Upgrade car attribute"""
        oid = _safe_object_id(car_id)
        mongo_db.cars.update_one(
            {'_id': oid if oid else car_id},
            {
                '$inc': {upgrade_type: amount},
                '$set': {'updated_at': datetime.now()}
            }
        )
        return CarDB.get_car(car_id)

class LevelDB:
    """Level Database Operations"""

    @staticmethod
    def initialize_levels():
        """Initialize game levels"""
        levels = [
            {
                'level_number': 1,
                'name': 'City Streets',
                'difficulty': 'easy',
                'track_length': 5000,
                'opponents': 3,
                'time_limit': 180,
                'rewards': {'coins': 100, 'exp': 50},
                'environment': {
                    'weather': 'sunny',
                    'time_of_day': 'day',
                    'obstacles': ['trees', 'buildings']
                }
            },
            {
                'level_number': 2,
                'name': 'Highway Rush',
                'difficulty': 'medium',
                'track_length': 7500,
                'opponents': 5,
                'time_limit': 240,
                'rewards': {'coins': 200, 'exp': 100},
                'environment': {
                    'weather': 'cloudy',
                    'time_of_day': 'afternoon',
                    'obstacles': ['traffic', 'barriers']
                }
            },
            {
                'level_number': 3,
                'name': 'Mountain Pass',
                'difficulty': 'hard',
                'track_length': 10000,
                'opponents': 7,
                'time_limit': 300,
                'rewards': {'coins': 300, 'exp': 150},
                'environment': {
                    'weather': 'foggy',
                    'time_of_day': 'evening',
                    'obstacles': ['rocks', 'cliffs', 'animals']
                }
            },
            {
                'level_number': 4,
                'name': 'Desert Storm',
                'difficulty': 'hard',
                'track_length': 12000,
                'opponents': 8,
                'time_limit': 360,
                'rewards': {'coins': 400, 'exp': 200},
                'environment': {
                    'weather': 'sandstorm',
                    'time_of_day': 'sunset',
                    'obstacles': ['dunes', 'cacti']
                }
            },
            {
                'level_number': 5,
                'name': 'Night City',
                'difficulty': 'extreme',
                'track_length': 15000,
                'opponents': 10,
                'time_limit': 420,
                'rewards': {'coins': 500, 'exp': 250},
                'environment': {
                    'weather': 'rainy',
                    'time_of_day': 'night',
                    'obstacles': ['puddles', 'traffic', 'pedestrians']
                }
            },
            {
                'level_number': 6,
                'name': 'Mountain Road',
                'difficulty': 'hard',
                'track_length': 11000,
                'opponents': 6,
                'time_limit': 320,
                'rewards': {'coins': 350, 'exp': 180},
                'environment': {
                    'weather': 'foggy',
                    'time_of_day': 'afternoon',
                    'obstacles': ['trees', 'rocks', 'cliffs']
                }
            },
            {
                'level_number': 7,
                'name': 'Hilly Road',
                'difficulty': 'hard',
                'track_length': 12000,
                'opponents': 7,
                'time_limit': 340,
                'rewards': {'coins': 380, 'exp': 200},
                'environment': {
                    'weather': 'cloudy',
                    'time_of_day': 'evening',
                    'obstacles': ['trees', 'rocks', 'cliffs']
                }
            },
            {
                'level_number': 8,
                'name': 'Hill Road',
                'difficulty': 'hard',
                'track_length': 13000,
                'opponents': 8,
                'time_limit': 360,
                'rewards': {'coins': 420, 'exp': 220},
                'environment': {
                    'weather': 'windy',
                    'time_of_day': 'sunset',
                    'obstacles': ['trees', 'rocks', 'cliffs']
                }
            },
            {
                'level_number': 9,
                'name': 'Mountain Path',
                'difficulty': 'extreme',
                'track_length': 14000,
                'opponents': 9,
                'time_limit': 380,
                'rewards': {'coins': 460, 'exp': 240},
                'environment': {
                    'weather': 'foggy',
                    'time_of_day': 'night',
                    'obstacles': ['trees', 'rocks', 'cliffs']
                }
            }
        ]

        for level in levels:
            existing = mongo_db.levels.find_one({'level_number': level['level_number']})
            if not existing:
                mongo_db.levels.insert_one(level)

    @staticmethod
    def get_level(level_number):
        """Get level by number"""
        level = mongo_db.levels.find_one({'level_number': level_number})
        if level:
            level['_id'] = str(level['_id'])
        return level

    @staticmethod
    def get_all_levels():
        """Get all levels"""
        levels = list(mongo_db.levels.find().sort('level_number', 1))
        for level in levels:
            level['_id'] = str(level['_id'])
        return levels

class GameSessionDB:
    """Game Session Database Operations"""

    @staticmethod
    def create_session(player_id, level_number, car_id):
        """Create a new game session"""
        session = {
            'player_id': player_id,
            'level_number': level_number,
            'car_id': car_id,
            'start_time': datetime.now(),
            'end_time': None,
            'duration': 0,
            'position': 0,
            'score': 0,
            'collisions': 0,
            'nitro_used': 0,
            'status': 'active',
            'completed': False
        }
        result = mongo_db.game_sessions.insert_one(session)
        session['_id'] = str(result.inserted_id)
        return session

    @staticmethod
    def update_session(session_id, update_data):
        """Update game session"""
        oid = _safe_object_id(session_id)
        mongo_db.game_sessions.update_one(
            {'_id': oid if oid else session_id},
            {'$set': update_data}
        )
        return GameSessionDB.get_session(session_id)

    @staticmethod
    def get_session(session_id):
        """Get session by ID"""
        oid = _safe_object_id(session_id)
        session = mongo_db.game_sessions.find_one({'_id': oid if oid else session_id})
        if session:
            session['_id'] = str(session['_id'])
        return session

    @staticmethod
    def complete_session(session_id, position, score):
        """Complete a game session"""
        update_data = {
            'end_time': datetime.now(),
            'position': position,
            'score': score,
            'status': 'completed',
            'completed': True
        }
        return GameSessionDB.update_session(session_id, update_data)

class LeaderboardDB:
    """Leaderboard Database Operations"""

    @staticmethod
    def add_score(player_id, level_number, score, time):
        """Add score to leaderboard"""
        entry = {
            'player_id': player_id,
            'level_number': level_number,
            'score': score,
            'time': time,
            'created_at': datetime.now()
        }

        # Check if player has existing score for this level
        existing = mongo_db.leaderboard.find_one({
            'player_id': player_id,
            'level_number': level_number
        })

        if existing:
            # Update if new score is better
            if score > existing['score']:
                mongo_db.leaderboard.update_one(
                    {'_id': existing['_id']},
                    {'$set': entry}
                )
        else:
            mongo_db.leaderboard.insert_one(entry)

    @staticmethod
    def get_leaderboard(level_number=None, limit=10):
        """Get leaderboard entries"""
        query = {'level_number': level_number} if level_number else {}
        entries = list(mongo_db.leaderboard.find(query).sort('score', -1).limit(limit))

        # Get player details
        for entry in entries:
            entry['_id'] = str(entry['_id'])
            player = PlayerDB.get_player(entry['player_id'])
            if player:
                entry['username'] = player['username']

        return entries
