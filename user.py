
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired
from flask_login import UserMixin
import api


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)


class User(UserMixin):

    def __init__(self, username, password):
        self.username = username
        self.password = self.get_password()
        self.id = self.get_id()

    def verify_password(self, password):
        if self.password is None:
            return False
        return password == self.password

    def get_password(self):
        try:
            res = api.get_password(self.username)
        except Exception:
            return None
        return res

    def get_id(self):
        res = api.get_user_id(self.username)
        return res

    @staticmethod
    def get(user_id):
        if not user_id:
            return None
        username = api.get_username(user_id)
        password = api.get_password(username)
        return User(username, password)

