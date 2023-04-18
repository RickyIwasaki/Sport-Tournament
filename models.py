
from flask_sqlalchemy import SQLAlchemy
from bcrypt import gensalt, hashpw
from sqlalchemy.dialects.postgresql import ARRAY
from uuid import uuid4

######################################################################
database = SQLAlchemy()
def connect_database(app):
    database.app = app
    database.init_app(app)
    
################################################################
class User(database.Model):
    __tablename__ = 'users'

    id = database.Column(database.String(36), primary_key = True, default = str(uuid4()))
    username = database.Column(database.String(31), nullable = False, unique = True)
    email = database.Column(database.String(255), nullable = False, unique = True)
    hashed_password = database.Column(database.String(60), nullable = False, unique = True)
    salt = database.Column(database.String(29), nullable = False, unique = True)
    region = database.Column(database.String(127))
    bio = database.Column(database.String(511))
    sport_list = database.Column(ARRAY(database.String(63)))

    teams = database.relationship('Team')
    teammates = database.relationship('Teammate')
    games = database.relationship('Game')
    tournaments = database.relationship('Tournament')

    @classmethod
    def check(self, username, email):
        existing_users = User.query.with_entities(User.username, User.email, User.salt).all()
        for existing_user in existing_users:
            if existing_user.username == username:
                return 'username already exists'
            if existing_user.email == email:
                return 'email already exists'

    @classmethod
    def create(self, username, email, password):        
        existing_users = User.query.with_entities(User.salt).all()
        
        while True:
            salt = gensalt(rounds = 14).decode('utf-8')
            if not any(salt == existing_user.salt for existing_user in existing_users):
                break
        hashed_password = hashpw(password.encode('utf-8'), salt.encode('utf-8')).decode('utf-8')

        user = User()
        is_new_id = False
        while is_new_id == False:
            user.id = str(uuid4())
            try:
                database.session.add(user)
                is_new_id = True
            except:
                'ignore error: assigning new random id'
                
        user.username = username
        user.email = email
        user.hashed_password = hashed_password
        user.salt = salt

        database.session.add(user)
        database.session.commit()

        return user

    @classmethod
    def authenticate(self, username, password):
        user = User.query.filter_by(username = username).first()
        if user is None:
            return 'username does not exists'
        
        hashed_password = hashpw(password.encode('utf-8'), user.salt.encode('utf-8')).decode('utf-8')
        if user.hashed_password != hashed_password:
            return 'password is incorrect'

        return user

class Friend(database.Model):
    __tablename__ = 'friends'

    # database relationship doesn't work for users to friends
    id = database.Column(database.Integer, primary_key = True, autoincrement = True)
    user_1_id = database.Column(database.String(36))
    user_2_id = database.Column(database.String(36))
    status = database.Column(database.String(31), nullable = False)

################################################################
class Sport(database.Model):
    __tablename__ = 'sports'

    id = database.Column(database.Integer, primary_key = True, autoincrement = True)
    name = database.Column(database.String(64), nullable = False, unique = True)
    description = database.Column(database.String(512), nullable = False)
    
    games = database.relationship('Game')

################################################################
class Team(database.Model):
    __tablename__ = 'teams'

    id = database.Column(database.String(36), primary_key = True, default = str(uuid4()))
    name = database.Column(database.String(32), nullable = False)
    description = database.Column(database.String(512))
    team_creator = database.Column(database.String(36), database.ForeignKey('users.id'))
    status = database.Column(database.String(31), nullable = False)

    users = database.relationship('User')
    teammates = database.relationship('Teammate')
    games_to_teams = database.relationship('Game_to_Team')

    @classmethod 
    def create(self, name, status, creator_id, description):
        teams = Team.query.all()
        while True:
            id = str(uuid4())
            if not any(id == team.id for team in teams):
                break
        
        team = Team(id = id, name = name, description = description, team_creator = creator_id, status = status)
        database.session.add(team)
        database.session.commit()

class Teammate(database.Model):
    __tablename__ = 'teammates'

    id = database.Column(database.Integer, primary_key = True, autoincrement = True)
    team_id = database.Column(database.String(36), database.ForeignKey('teams.id'))
    user_id = database.Column(database.String(36), database.ForeignKey('users.id'))
    
    users = database.relationship('User')
    teams = database.relationship('Team')

################################################################
class Game(database.Model):
    __tablename__ = 'games'

    id = database.Column(database.String(36), primary_key = True, default = str(uuid4()))
    name = database.Column(database.String(64), nullable = False)
    sport_id = database.Column(database.Integer, database.ForeignKey('sports.id'))
    place = database.Column(database.String(128))
    set_time = database.Column(database.String(31))
    result = database.Column(database.String(64))
    game_creator_id = database.Column(database.String(36), database.ForeignKey('users.id'))
    status = database.Column(database.String(31), nullable = False)

    users = database.relationship('User')
    sports = database.relationship('Sport')
    games_to_teams = database.relationship('Game_to_Team')
    tournament_to_games = database.relationship('Tournament_to_game')

    @classmethod 
    def create(self, name, sport_id, place, set_time, game_creator_id, status):
        games = Game.query.all()
        while True:
            id = str(uuid4())
            if not any(id == game.id for game in games):
                break
        
        game = Game(id = id, name = name, sport_id = sport_id, place = place, set_time = set_time, game_creator_id = game_creator_id, status = status)
        database.session.add(game)
        database.session.commit()

        return game

class Game_to_Team(database.Model):
    __tablename__ = 'games_to_teams'

    id = database.Column(database.Integer, primary_key = True, autoincrement = True)
    game_id = database.Column(database.String(36), database.ForeignKey('games.id'))
    team_id = database.Column(database.String(36), database.ForeignKey('teams.id'))
    status = database.Column(database.String(31), nullable = False)

    games = database.relationship('Game')
    teams = database.relationship('Team')

################################################################
class Tournament_type(database.Model):
    __tablename__ = 'tournament_types'

    id = database.Column(database.Integer, primary_key = True, autoincrement = True)
    name = database.Column(database.String(32), nullable = False, unique = True)
    statuses = database.Column(ARRAY(database.String(64)), nullable = False)

    tournaments = database.relationship('Tournament')

class Tournament(database.Model):
    __tablename__ = 'tournaments'

    id = database.Column(database.String(36), primary_key = True, default = str(uuid4()))
    name = database.Column(database.String(64), nullable = False)
    description = database.Column(database.String(512))
    type_id = database.Column(database.Integer, database.ForeignKey('tournament_types.id'))
    tournament_creator_id = database.Column(database.String(36), database.ForeignKey('users.id'))
    status = database.Column(database.String(31), nullable = False)

    users = database.relationship('User')
    tournament_types = database.relationship('Tournament_type')
    tournament_to_games = database.relationship('Tournament_to_game')

    @classmethod
    def create(self, name, description, type_id, tournament_creator_id, status):
        tournaments = Tournament(name = name, description = description, type_id = type_id, tournament_creator_id = tournament_creator_id, status = status)
        while True:
            tournaments.id = str(uuid4())
            try:
                database.session.add(tournaments)
                database.session.commit()
                break
            except:
                'ignore error: reassigning new random id'

class Tournament_to_game(database.Model):
    __tablename__ = 'tournament_to_games'

    id = database.Column(database.Integer, primary_key = True, autoincrement = True)
    tournament_id = database.Column(database.String(36), database.ForeignKey('tournaments.id'))
    game_id = database.Column(database.String(36), database.ForeignKey('games.id'))
    status = database.Column(database.String(64), nullable = False)
    
    games = database.relationship('Game')
    tournaments = database.relationship('Tournament')
