from flask import render_template, url_for, flash, redirect, Blueprint
from flask_login import login_required

from flask_app import db
from flask_app.models import Accueilli, Accueillant, Email_OP
from flask_app.boucles_accueil.forms import AccueilliInfoForm
from flask_app.accueillants.utils_mailer import get_conversations
from flask_app.accueillants.forms import SendMailForm

boucles_accueil = Blueprint('boucles_accueil', '__name__')


@boucles_accueil.route('/liste_accueillis')
@login_required
def liste_accueillis():
    accueillis = Accueilli.query.all()
    liste_accueillants = Accueillant.query.all()
    dict_emails = get_conversations(Email_OP.query.distinct())

    # Send email
    form = SendMailForm()
    if form.validate_on_submit():
        send_email_simple(
            'florian.dadouchi@gmail.com', form.body.data, 'test formulaire')

    return render_template('liste_accueillis.html', accueillis=accueillis,
                           accueillants=liste_accueillants,
                           emails=dict_emails,
                           form=form)


@boucles_accueil.route('/accueilli/new', methods=['GET', 'POST'])
@login_required
def new_accueilli():
    form = AccueilliInfoForm()
    if form.validate_on_submit():
        accueilli = Accueilli(nom=form.nom.data,
                              email=form.email.data,
                              tel=form.tel.data,
                              remarques=form.remarques.data)
        db.session.add(accueilli)
        db.session.commit()
        flash(f'Accueilli créé : {accueilli.nom}', 'success')
        return redirect(url_for('boucles_accueil.liste_accueillis'))
    return render_template('accueilli_infos.html',
                           title='create_modif_accueilli',
                           legend='Nouvel Accueilli',
                           form=form)
