from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from flask_app.models import Coordinateur


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Coordo ?')

    def validate_username(self, username):
        user_query = Coordinateur.query.filter_by(nom=username.data).first()
        if user_query:
            raise ValidationError("Nom d'utilisateur déjà pris")

    def validate_email(self, email):
        email_query = Coordinateur.query.filter_by(email=email.data).first()
        if email_query:
            raise ValidationError("Email déjà existant")


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me ?')
    submit = SubmitField('Login!')
