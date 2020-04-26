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
    submit = SubmitField("S'enregistrer comme coordo")

    def validate_username(self, username):
        user_query = Coordinateur.query.filter_by(nom=username.data).first()
        if user_query:
            raise ValidationError("Nom d'utilisateur déjà pris")


class AddCoordoForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField("Envoyer un mail d'invitation")

    def validate_email(self, email):
        email_query = Coordinateur.query.filter_by(email=email.data).first()
        if email_query:
            raise ValidationError("Coordinateur existant")


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me ?')
    submit = SubmitField('Login!')


class RequestResetPassword(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Réinitialiser mot de passe')

    def validate_email(self, email):
        email_query = Coordinateur.query.filter_by(email=email.data).first()
        if email_query is None:
            raise ValidationError("Pas de compte associé à cet email.")


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Changer le mot de passe')
