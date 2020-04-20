from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired


class AccueillantInfoForm(FlaskForm):
    disponibilite = StringField('Disponibilité')
    nom = StringField('Nom', validators=[DataRequired()])
    tel = StringField('Téléphone')
    adresse = StringField('Adresse')
    email = StringField('Email')
    accueillis = SelectMultipleField(u'Accueilli', choices=[])
    next_action = TextAreaField('Prochaine Action')
    remarques = TextAreaField('Remarques')
    submit = SubmitField("OK")


class SendMailForm(FlaskForm):
    body = TextAreaField('Message', validators=[DataRequired()])
    object_ = StringField('Objet', validators=[DataRequired()])
    destinataire = StringField('Destinataire', validators=[DataRequired()])
    destinataire_copie = StringField('CC')
    submit = SubmitField('Envoyer')
