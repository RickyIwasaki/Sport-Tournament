from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length

from models import Tournament_type

######################################################################
class Signin_form(FlaskForm):
    username = StringField('username', validators = [DataRequired()])
    email = StringField('email', validators = [DataRequired(), Email()])
    password = PasswordField('password', validators = [Length(min = 6)])

class Login_form(FlaskForm):
    username = StringField('username', validators = [DataRequired()])
    password = PasswordField('password', validators = [Length(min = 6)])

class Edit_user_form(FlaskForm):
    username = StringField('username', validators = [DataRequired()])
    email = StringField('email', validators = [DataRequired(), Email()])
    bio = TextAreaField('describe your plays')
    password = PasswordField('password', validators = [Length(min = 6)])

class Sport_form(FlaskForm):
    name = StringField('sport', validators = [DataRequired()])
    description = TextAreaField('sport description', validators = [DataRequired()])

class Team_form(FlaskForm):
    name = StringField('team', validators = [DataRequired()])
    status = SelectField('status', choices = ['publicly open', 'private'])
    description = TextAreaField('team description', validators = [DataRequired()])
