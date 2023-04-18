
from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
import os
import requests
from threading import Thread
import datetime
import time

from secret import database_name, database_user_username, database_user_password, app_secret_key, developer_id, news_api_key
from forms import Signin_form, Login_form, Edit_user_form, Sport_form, Team_form
from models import database, connect_database, User, Tournament_type, Tournament, Sport, Game, Tournament_to_game, Team, Friend, Game_to_Team, Teammate

################################################################################
app = Flask(__name__)

database_connection_uri = f"postgresql://{ database_user_username }:{ database_user_password }@localhost/{ database_name }"
os_database_connection_uri = os.environ.get('DATABASE_DEFAULT_URI', database_connection_uri)
app.config['SQLALCHEMY_DATABASE_URI'] = os_database_connection_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', app_secret_key)
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

toolbar = DebugToolbarExtension(app)
connect_database(app)

################################################################################
def update_sport_news():
    url = f"https://newsapi.org/v2/top-headlines?country=us&category=sports&apiKey={news_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        sport_news_data = response.articles

def background_task():
    while True:
        now = datetime.datetime.now().time()
        if now >= datetime.time(10, 30) and now <= datetime.time(11, 0):
            update_sport_news()
        time.sleep(1)

background_thread = Thread(target = background_task)

################################################################################
@app.before_request
def set_current_user():
    if 'current_user_id' in session:
        g.current_user = User.query.filter_by(id = session['current_user_id']).first()
    else: 
        g.current_user = None

@app.route('/signin', methods=['GET', 'POST'])
def signin_route():
    form = Signin_form()
    if request.method != 'POST' or not form.validate_on_submit():
        return render_template('users/signin.html', form = form)

    result = User.check(form.username.data, form.email.data)
    if result == 'username already exists' or result == 'email already exists':
        return render_template('users/signin.html', form = form, result_error = result)
    user = User.create(form.username.data, form.email.data, form.password.data)
    login(user.id)

    return redirect("/")

def login(user_id):
    session['current_user_id'] = user_id

@app.route('/login', methods=['GET', 'POST'])
def login_route():
    form = Login_form()
    if request.method != 'POST' or not form.validate_on_submit():
        return render_template('users/login.html', form = form)

    user = User.authenticate(form.username.data, form.password.data)
    if user == 'username does not exists' or user == 'password is incorrect':
        return render_template('users/login.html', form = form, result_error = user)
    login(user.id)

    return redirect("/")

def logout():
    if 'current_user_id' in session:
        del session['current_user_id']

@app.route('/logout')
def logout_route():
    logout()
    return redirect('/login')

################################################################################
@app.route('/')
def base_route():
    if not 'current_user_id' in session:
        return redirect('/welcome')
    return redirect('/home')

@app.route('/welcome')
def welcome_route():
    if 'current_user_id' in session:
        return redirect('/home')
    return render_template('front.html')

@app.route('/home')
def home_route():
    if not 'current_user_id' in session:
        return redirect('/login')
    return render_template('home.html', is_developer = (developer_id == f"{g.current_user.id}"))

@app.route('/home/api')
def home_api_route():
    if not 'current_user_id' in session:
        return redirect('/login')

    url = f"https://newsapi.org/v2/top-headlines?country=us&category=sports&apiKey={news_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        sport_news_data = response.json()
        return sport_news_data

################################################################################
@app.route('/tournament_types')
def tournament_types_route():
    if f"{g.current_user.id}" != developer_id:
        return 'no your not a developer'

    tournament_types = Tournament_type.query.all()
    return render_template('tournament_types/tournament_types.html', is_developer = (developer_id == f"{g.current_user.id}"), tournament_types = tournament_types)

@app.route('/tournament_types/create', methods = ['GET', 'POST'])
def tournament_types_create_route():
    if f"{g.current_user.id}" != developer_id:
        return 'no your not a developer'
    if request.method != 'POST':
        return render_template('tournament_types/tournament_type_create.html', is_developer = (developer_id == f"{g.current_user.id}"))

    tournament_type = Tournament_type.query.filter_by(name = request.form['tournament_type']).first()
    if not tournament_type is None:
        return redirect('/tournament_types')

    statuses = []
    for key in request.form:
        statuses.append(request.form[key])
    statuses = statuses[1:]

    new_tournament_type = Tournament_type(name = request.form['tournament_type'], statuses = statuses)
    database.session.add(new_tournament_type)
    database.session.commit()

    return redirect('/tournament_types')

@app.route('/tournament_types/<tournament_type_id>', methods = ['GET', 'POST'])
def tournament_type_route(tournament_type_id):
    if f"{g.current_user.id}" != developer_id:
        return 'no your not a developer'

    tournament_type = Tournament_type.query.filter_by(id = tournament_type_id).first()
    if request.method != 'POST':
        return render_template('tournament_types/tournament_type.html', is_developer = (developer_id == f"{g.current_user.id}"), tournament_type = tournament_type)

    statuses = []
    for key in request.form:
        statuses.append(request.form[key])
    tournament_type.statuses = statuses
    database.session.add(tournament_type)
    database.session.commit()

    return redirect('/tournament_types')
    
@app.route('/tournament_types/delete/<tournament_type_id>')
def tournament_type_delete_route(tournament_type_id):
    if f"{g.current_user.id}" != developer_id:
        return 'no your not a developer'

    tournament_type = Tournament_type.query.filter_by(id = tournament_type_id).first()
    database.session.delete(tournament_type)
    database.session.commit()

    return redirect('/tournament_types')

@app.route('/tournament_types/api/tournament/<tournament_id>')
def tournament_type_api_route(tournament_id):
    if not 'current_user_id' in session:
        return 'no'

    tournament = Tournament.query.filter_by(id = tournament_id).first()
    tournament_type = Tournament_type.query.filter_by(id = tournament.type_id).first()
    return tournament_type.statuses

################################################################################
@app.route('/tournaments')
def tournaments_route():
    if not 'current_user_id' in session:
        return redirect('/login')
    return render_template('tournaments/tournaments.html', is_developer = (developer_id == f"{g.current_user.id}"))

@app.route('/tournaments/api/<filter>')
def tournaments_api_route(filter):
    if not 'current_user_id' in session:
        return 'no'

    # filter is all of the conditions (publicly open/close, friends open/close, search, tournament type, tournament id, tournament creator id)
    statuses = filter.split(',')
    tournaments = []
    if 'publicly open' in statuses:
        tournaments += Tournament.query.filter_by(status = 'publicly open').all()
    if 'private' in statuses:
        tournaments += Tournament.query.filter_by(tournament_creator_id = g.current_user.id, status = 'private').all()
    
    users = User.query.with_entities(User.id, User.username).all()
    user_ids_to_usernames  = {}
    for user in users:
        user_ids_to_usernames[user.id] = user.username
    
    tournament_types = Tournament_type.query.with_entities(Tournament_type.id, Tournament_type.name).all()
    tournament_type_ids_to_names = {}
    for tournament_type in tournament_types:
        tournament_type_ids_to_names[tournament_type.id] = tournament_type.name

    temp_tournaments = []
    for tournament in tournaments:
        temp_tournament = []
        temp_tournament.append(tournament.name)
        temp_tournament.append(tournament.id)
        temp_tournament.append(tournament_type_ids_to_names[tournament.type_id])
        temp_tournament.append(user_ids_to_usernames[tournament.tournament_creator_id])
        temp_tournament.append(tournament.status)
        temp_tournaments.append(temp_tournament)
    tournaments = temp_tournaments

    return tournaments

@app.route('/tournaments/create', methods = ['GET', 'POST'])
def tournament_create_route():
    if not 'current_user_id' in session:
        return redirect('/login')

    tournament_types = Tournament_type.query.with_entities(Tournament_type.name).all()
    statuses = ['publicly open', 'private']

    if request.method != 'POST':
        return render_template('tournaments/tournament_create.html', is_developer = (developer_id == f"{g.current_user.id}"), tournament_types = tournament_types, statuses = statuses, result_error = '')
    if request.form['name'] == '':
        return render_template('tournaments/tournament_create.html', is_developer = (developer_id == f"{g.current_user.id}"), tournament_types = tournament_types, statuses = statuses, result_error = 'fill tournament name')

    tournament_type = Tournament_type.query.filter_by(name = request.form['tournament_type']).first()
    Tournament.create(request.form['name'], request.form['description'], tournament_type.id, f"{g.current_user.id}", request.form['status'])

    return redirect("/tournaments")

@app.route('/tournaments/<tournament_id>')
def tournament_route(tournament_id):
    if not 'current_user_id' in session:
        return redirect('/login')

    tournament = Tournament.query.filter_by(id = tournament_id).first()
    tournament_type = Tournament_type.query.filter_by(id = tournament.type_id).first()
    user = User.query.filter_by(id = tournament.tournament_creator_id).first()
    games = Tournament_to_game.query.filter_by(tournament_id = tournament_id).join(Game).filter(Tournament_to_game.game_id == Game.id).with_entities(Game.id, Game.name, Game.result, Tournament_to_game.status).all()

    return render_template('tournaments/tournament.html', is_developer = (developer_id == f"{g.current_user.id}"), is_creator = (user.id == g.current_user.id), tournament = tournament, tournament_type = tournament_type.name, creator = user.username, games = games)

@app.route('/tournaments/edit/<tournament_id>', methods = ['GET', 'POST'])
def tournament_edit_route(tournament_id):
    tournament = Tournament.query.filter_by(id = tournament_id).first()
    if tournament is None:
        return 
    user = User.query.filter_by(id = tournament.tournament_creator_id).first()
    if g.current_user.id != user.id:
        return redirect('/tournaments')

    tournament_types = Tournament_type.query.all()
    statuses = ['publicly open', 'private']

    if request.method != 'POST':
        return render_template('tournaments/tournament_edit.html', is_developer = (developer_id == f"{g.current_user.id}"), tournament = tournament, tournament_types = tournament_types, statuses = statuses)
    
    tournament_type = Tournament_type.query.filter_by(name = request.form['tournament_type']).first()
    tournament.name = request.form['name']
    tournament.description = request.form['description']
    tournament.type_id = tournament_type.id
    tournament.tournament_creator_id = g.current_user.id
    tournament.status = request.form['status']
    database.session.add(tournament)
    database.session.commit()

    return redirect('/tournaments')

@app.route('/tournaments/delete/<tournament_id>')
def tournament_delete_route(tournament_id):
    # future bugs can't delete tournaments that already have games assigned
    tournament = Tournament.query.filter_by(id = tournament_id).first()
    if tournament is None:
        return 
    user = User.query.filter_by(id = tournament.tournament_creator_id).first()

    if g.current_user.id == user.id:
        database.session.delete(tournament)
        database.session.commit()

    return redirect('/tournaments')

################################################################################
@app.route('/sports')
def sports_route():
    if f"{g.current_user.id}" != developer_id:
        return 'no your not a developer'

    sports = Sport.query.all()
    return render_template('sports/sports.html', is_developer = (developer_id == f"{g.current_user.id}"), sports = sports)

@app.route('/sports/create', methods = ['GET', 'POST'])
def sport_create_route():
    if f"{g.current_user.id}" != developer_id:
        return 'no your not a developer'

    form = Sport_form()
    print('------------------')
    print(request.method)
    print(request.method != 'POST')
    print(not form.validate_on_submit())
    if request.method != 'POST':
        return render_template('sports/sport_create_edit.html', is_developer = (developer_id == f"{g.current_user.id}"), form = form, sport_id = 0)
    
    sport = Sport(name = form.name.data, description = form.description.data)
    database.session.add(sport)
    database.session.commit()

    return redirect('/sports')

@app.route('/sports/<sport_id>', methods = ['GET', 'POST'])
def sport_route(sport_id):
    if f"{g.current_user.id}" != developer_id:
        return 'no your not a developer'

    sport = Sport.query.filter_by(id = sport_id).first()
    if sport is None:
        return 

    form = Sport_form()
    if request.method != 'POST' or form.name.data == '' or form.description.data == '':
        form.name.data = sport.name
        form.description.data = sport.description
        return render_template('sports/sport_create_edit.html', is_developer = (developer_id == f"{g.current_user.id}"), form = form, sport_id = sport_id)
    
    sport.name = form.name.data
    sport.description = form.description.data
    database.session.add(sport)
    database.session.commit()

    return redirect('/sports')

@app.route('/sports/delete/<sport_id>')
def sport_delete_route(sport_id):
    if f"{g.current_user.id}" != developer_id:
        return 'no your not a developer'

    sport = Sport.query.filter_by(id = sport_id).first()
    database.session.delete(sport)
    database.session.commit()

    return redirect('/sports')

################################################################################
@app.route('/games')
def games_route():
    if not 'current_user_id' in session:
        return redirect('/login')
    return render_template('games/games.html', is_developer = (developer_id == f"{g.current_user.id}"))

@app.route('/games/api/<filter>')
def games_api_route(filter):
    if not 'current_user_id' in session:
        return 'no'

    # filter is all of the conditions (publicly open/close, friends open/close, search, location, game id, game creator id)
    statuses = filter.split(',')
    games = []
    if 'publicly open' in statuses:
        games += Game.query.filter_by(status = 'publicly open').all()
    if 'private' in statuses:
        games += Game.query.filter_by(game_creator_id = g.current_user.id, status = 'private').all()
    
    users = User.query.with_entities(User.id, User.username).all()
    user_ids_to_usernames  = {}
    for user in users:
        user_ids_to_usernames[user.id] = user.username

    temp_games = []
    for game in games:
        tournament_to_game = Tournament_to_game.query.filter_by(game_id = game.id).first()
        touranment = Tournament.query.filter_by(id = tournament_to_game.tournament_id).first()
        tournament_type = Tournament_type.query.filter_by(id = touranment.type_id).first()
        sport = Sport.query.filter_by(id = game.sport_id).first()

        temp_game = []
        temp_game.append(game.name)
        temp_game.append(game.id)
        temp_game.append(touranment.name)
        temp_game.append(tournament_type.name)
        temp_game.append(sport.name)
        temp_game.append(user_ids_to_usernames[game.game_creator_id])
        temp_game.append(game.status)
        temp_games.append(temp_game)
    games = temp_games

    return games

@app.route('/games/create', methods = ['GET', 'POST'])
def game_create_route():
    if not 'current_user_id' in session:
        return redirect('/login')

    sports = Sport.query.with_entities(Sport.name).all()
    statuses = ['publicly open', 'private']
    tournaments = Tournament.query.filter_by(tournament_creator_id = g.current_user.id).all()
    
    if request.method != 'POST':
        return render_template('games/game_create.html', is_developer = (developer_id == f"{g.current_user.id}"), sports = sports, statuses = statuses, tournaments = tournaments, result_error = '')

    if request.form['name'] == '':
        return render_template('games/game_create.html', is_developer = (developer_id == f"{g.current_user.id}"), sports = sports, statuses = statuses, tournaments = tournaments, result_error = 'fill game name')

    sport = Sport.query.filter_by(name = request.form['sport']).first()
    game = Game.create(request.form['name'], sport.id, request.form['place'], request.form['time'], g.current_user.id, request.form['status'])
    tournament_to_game = Tournament_to_game(tournament_id = request.form['tournament'][:request.form['tournament'].index(' :')], game_id = game.id, status = request.form['tournament_game_status'])

    database.session.add(tournament_to_game)
    database.session.commit()

    return redirect('/games')

@app.route('/games/<game_id>')
def game_route(game_id):
    if not 'current_user_id' in session:
        return redirect('/login')

    game = Game.query.filter_by(id = game_id).first()
    user = User.query.filter_by(id = game.game_creator_id).first()
    sport = Sport.query.filter_by(id = game.sport_id).first()
    tournament_to_game = Tournament_to_game.query.filter_by(game_id = game.id).first()
    tournament = Tournament.query.filter_by(id = tournament_to_game.tournament_id).first()
    tournament_type = Tournament_type.query.filter_by(id = tournament.type_id).first()
    teams = Game_to_Team.query.filter_by(game_id = game_id).join(Team).filter(Game_to_Team.team_id == Team.id).with_entities(Team.name, Team.id).all()    

    return render_template('games/game.html', is_developer = (developer_id == f"{g.current_user.id}"), is_creator = (user.id == g.current_user.id), game = game, user = user, sport = sport, tournament_to_game = tournament_to_game, tournament = tournament, tournament_type = tournament_type, teams = teams)

@app.route('/games/edit/<game_id>', methods = ['GET', 'POST'])
def game_edit_route(game_id):
    if not 'current_user_id' in session:
        return redirect('/login')

    game = Game.query.filter_by(id = game_id).first()
    user = User.query.filter_by(id = game.game_creator_id).first()
    if user.id != g.current_user.id:
        return 'no'

    sports = Sport.query.all()
    statuses = ['publicly open', 'publicly close', 'friends open', 'friends close', 'private']
    tournaments = Tournament.query.filter_by(tournament_creator_id = g.current_user.id).all()
    tournament_to_game = Tournament_to_game.query.filter_by(game_id = game.id).first()

    if request.method != 'POST':
        return render_template('games/game_edit.html', is_developer = (developer_id == f"{g.current_user.id}"), game = game, sports = sports, statuses = statuses, tournaments = tournaments, tournament_to_game = tournament_to_game, result_error = '')

    if request.form['name'] == '':
        return render_template('games/game_edit.html', is_developer = (developer_id == f"{g.current_user.id}"), game = game, sports = sports, statuses = statuses, tournaments = tournaments, tournament_to_game = tournament_to_game,  result_error = 'fill game name')

    sport = Sport.query.filter_by(name = request.form['sport']).first()

    game.name = request.form['name']
    game.sport_id = sport.id
    game.place = request.form['place']
    game.set_time = request.form['time']
    game.game_creator_id = g.current_user.id
    game.status = request.form['status']
    
    tournament_to_game.touranment_id = request.form['tournament'][:request.form['tournament'].index(' :')]
    database.session.add(tournament_to_game)
    database.session.commit()

    return redirect('/games')

@app.route('/games/delete/<game_id>')
def game_delete_route(game_id):
    if not 'current_user_id' in session:
        return redirect('/login')

    game = Game.query.filter_by(id = game_id).first()
    user = User.query.filter_by(id = game.game_creator_id).first()

    if user.id != g.current_user.id:
        return 'no'

    # tournaments_to_game = Tournament_to_game.query.filter_by(game_id = game.id).all()
    # database.session.delete(tournaments_to_game)
    # database.session.commit()

    database.session.delete(game)
    database.session.commit()

    return redirect('/teams')

@app.route('/games/join/<game_id>', methods = ['GET', 'POST'])
def game_join_route(game_id):
    if not 'current_user_id' in session:
        return redirect('/login')

    teams = Teammate.query.filter_by(user_id = g.current_user.id).join(User).filter(Teammate.user_id == User.id).with_entities(Team.name, Team.id).all()
    if request.method != 'POST':
        return render_template('games/join.html', is_developer = (developer_id == f"{g.current_user.id}"), teams = teams)

    team = Team.query.filter_by(id = request.form['team'][:request.form['team'].index(' :')]).first()
    game_to_team = Game_to_Team(game_id = game_id, team_id = team.id, status = 'joined')
    database.session.add(game_to_team)
    database.session.commit()

    return redirect(f"/games/{ game_id }")
        

################################################################################
@app.route('/teams')
def teams_route():
    if not 'current_user_id' in session:
        return redirect('/login')
    return render_template('teams/teams.html', is_developer = (developer_id == f"{g.current_user.id}"))

@app.route('/teams/api/<filter>')
def teams_api_route(filter):
    if not 'current_user_id' in session:
        return 'no'

    # filter is all of the conditions (publicly open/close, friends open/close, search, team name, team id, team creator id)
    statuses = filter.split(',')
    teams = []
    if 'publicly open' in statuses:
        teams += Team.query.filter_by(status = 'publicly open').all()
    if 'private' in statuses:
        teams += Team.query.filter_by(team_creator = g.current_user.id, status = 'private').all()
    
    users = User.query.with_entities(User.id, User.username).all()
    user_ids_to_usernames  = {}
    for user in users:
        user_ids_to_usernames[user.id] = user.username

    temp_teams = []
    for team in teams:
        temp_team = []
        temp_team.append(team.name)
        temp_team.append(team.id)
        temp_team.append(user_ids_to_usernames[team.team_creator])
        temp_team.append(team.status)
        temp_teams.append(temp_team)
    teams = temp_teams

    return teams

@app.route('/teams/create', methods = ['GET', 'POST'])
def team_create_route():
    if not 'current_user_id' in session:
        return redirect('/login')

    form = Team_form()

    if request.method != 'POST' or not form.validate_on_submit():
        return render_template('teams/team_create.html', is_developer = (developer_id == f"{g.current_user.id}"), form = form)

    Team.create(form.name.data, form.status.data, g.current_user.id, form.description.data)
    
    return redirect('/teams')

@app.route('/teams/<team_id>')
def team_route(team_id):
    if not 'current_user_id' in session:
        return redirect('/login')

    team = Team.query.filter_by(id = team_id).first()
    user = User.query.filter_by(id = team.team_creator).first()
    teammates = Teammate.query.filter_by(team_id = team_id).join(User).filter(Teammate.user_id == User.id).with_entities(Teammate.user_id, User.username).all()

    return render_template('teams/team.html', is_developer = (developer_id == f"{g.current_user.id}"), is_creator = (team.team_creator == g.current_user.id), team = team, user = user, teammates = teammates)

@app.route('/teams/edit/<team_id>', methods = ['GET', 'POST'])
def team_edit_route(team_id):
    if not 'current_user_id' in session:
        return redirect('/login')

    team = Team.query.filter_by(id = team_id).first()
    user = User.query.filter_by(id = team.team_creator).first()

    if user.id != g.current_user.id:
        return 'no'

    form = Team_form()

    if request.method != 'POST' or not form.validate_on_submit():
        form.name.data = team.name 
        form.description.data = team.description
        form.status.data = team.status
        return render_template('teams/team_edit.html', is_developer = (developer_id == f"{g.current_user.id}"), form = form, team = team)

    team.name = form.name.data
    team.description = form.description.data    
    team.status = form.status.data

    database.session.add(team)
    database.session.commit()

    return redirect('/teams')

@app.route('/teams/delete/<team_id>')
def team_delete_route(team_id):
    if not 'current_user_id' in session:
        return redirect('/login')

    team = Team.query.filter_by(id = team_id).first()
    user = User.query.filter_by(id = team.team_creator).first()

    if user.id != g.current_user.id:
        return 'no'

    database.session.delete(team)
    database.session.commit()

    return redirect('/teams')

@app.route('/teams/join/<team_id>')
def team_join_route(team_id):
    if not 'current_user_id' in session:
        return redirect('/login')

    teammate = Teammate.query.filter_by(team_id = team_id, user_id = g.current_user.id).first()
    if teammate is None:
        teammate = Teammate(team_id = team_id, user_id = g.current_user.id)
        database.session.add(teammate)
        database.session.commit()
    
    return redirect(f"/teams/{ team_id }")

################################################################################
# @app.route('/users')
# def users_route():
#     if not 'current_user_id' in session:
#         return redirect('/login')
#     return render_template('users/users.html', is_developer = (developer_id == f"{g.current_user.id}"))

# @app.route('/users/api/<filter>')
# def users_api_route(filter):
#     if not 'current_user_id' in session:
#         return redirect('/login')

#     if filter == 'true':
#         users = User.query.all()

#         temp_users = []
#         for user in users:
#             temp_user = []
#             temp_user.append(user.id)
#             temp_user.append(user.username)
#             temp_user.append(user.region)
#             temp_users.append(temp_user)
#         users = temp_users

#         return users
#     else:
#         users = []
#         temp_users = []

#         friends = Friend.query.filter_by(user_1_id = g.current_user.id).all()
#         for friend in friends:
#             user = User.query.filter_by(id = friends.user_2_id).first() 
#             temp_user = []
#             temp_user.append(user.id)
#             temp_user.append(user.username)
#             temp_user.append(user.region)
#             temp_user.append(friend.status)
#             temp_users.append(temp_user)

#         friends = Friend.query.filter_by(user_2_id = g.current_user.id).all()
#         for friend in friends:
#             user = User.query.filter_by(id = friends.user_1_id).first() 
#             temp_user = []
#             temp_user.append(user.id)
#             temp_user.append(user.username)
#             temp_user.append(user.region)
#             temp_user.append(friend.status)
#             temp_users.append(temp_user)
#         users = temp_users

#         return users

# @app.route('/users/<user_id>')
# def user_route(user_id):
#     if not 'current_user_id' in session:
#         return redirect('/login')

#     user = User.query.filter_by(id = user_id).first()

#     friend = Friend.query.filter_by(user_1_id = user.id).first()
#     if not friend is None:
#         return render_template('users/user.html', is_developer = (developer_id == f"{g.current_user.id}"), user = user, friend = friend)
#     friend = Friend.query.filter_by(user_2_id = user.id).first()
#     if not friend is None:
#         return render_template('users/user.html', is_developer = (developer_id == f"{g.current_user.id}"), user = user, friend = friend)

#     return render_template('users/user.html', is_developer = (developer_id == f"{g.current_user.id}"), user = user, friend = False)
    
# @app.route('/friends/request/<user_id>')
# def user_request_route(user_id):
#     if not 'current_user_id' in session:
#         return redirect('/login')

# @app.route('/friends/cancel/<user_id>')
# def user_cancel_route(user_id):
#     if not 'current_user_id' in session:
#         return redirect('/login')

# @app.route('/friends/unfriend/<user_id>')
# def user_unfriend_route(user_id):
#     if not 'current_user_id' in session:
#         return redirect('/login')



