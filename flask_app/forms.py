from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_app.models import Coordinateur

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                            validators=[DataRequired(), Length(min=2,max=20)])
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
    
class SendMailForm(FlaskForm):
    body = TextAreaField('Message', validators=[DataRequired()])
    object_ = StringField('Objet', validators=[DataRequired()])
    destinataire = StringField('Destinataire', validators=[DataRequired()])
    destinataire_copie = StringField('CC')
    submit = SubmitField('Envoyer')


class AccueillantInfoForm(FlaskForm):
    disponibilite = StringField('Disponibilité')
    nom = StringField('Nom', validators=[DataRequired()])
    tel = StringField('Téléphone')
    adresse = StringField('Adresse')
    email = StringField('Email')
    email = StringField('Email')
    accueillis = SelectMultipleField(u'Accueilli', choices=[])
    next_action = TextAreaField('Prochaine Action')
    remarques = TextAreaField('Remarques')    
    submit = SubmitField("OK")


class AccueilliInfoForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    tel = StringField('Téléphone')
    email = StringField('Email')
    remarques = TextAreaField('Remarques')    
    submit = SubmitField("OK")