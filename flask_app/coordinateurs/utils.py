from flask import url_for
from flask_app import mail
from flask_mail import Message
from env import LOP_LOGIN


def send_email_invitation(coordo):
    token = coordo.get_reset_token()
    msg = Message("Message d'invitation",
                  sender=LOP_LOGIN,
                  recipients=['florian.dadouchi@gmail.com'])
    msg.body = f''' Pour devenir coordinateur de l'Ouvre Porte :

    {url_for('coordinateurs.register', token=token, _external=True)}'''
    mail.send(msg)


def send_reset_email(coordo):
    token = coordo.get_reset_token()
    msg = Message('Réinitialisation de mot de passe',
                  sender=LOP_LOGIN,
                  recipients=['florian.dadouchi@gmail.com'])
    msg.body = f''' Pour réinitialiser votre mot de passe : {url_for('coordinateurs.reset_token', token=token, _external=True)}'''
    mail.send(msg)
