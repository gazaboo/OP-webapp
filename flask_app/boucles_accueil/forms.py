from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class AccueilliInfoForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    tel = StringField('Téléphone')
    email = StringField('Email')
    remarques = TextAreaField('Remarques')
    submit = SubmitField("OK")