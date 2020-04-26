from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField


class AccueilliInfoForm(FlaskForm):
    nom = StringField('Nom', validators=[DataRequired()])
    tel = StringField('Téléphone')
    email = StringField('Email')
    next_action = TextAreaField('Prochaine action')
    remarques = TextAreaField('Remarques')
    submit = SubmitField("OK")


class NewAccueilForm(FlaskForm):
    date_debut = DateField(
        'Début', format="%Y-%m-%d")
    date_fin = DateField(
        'Fin', format="%Y-%m-%d")
    accueillant = SelectField(u'Accueillant', coerce=int)
    remarque = TextAreaField('Remarque')
    submit = SubmitField("OK")
