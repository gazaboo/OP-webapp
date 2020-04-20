from flask import render_template, url_for, flash, redirect, Blueprint
from flask_login import login_required

from flask_app import db
from flask_app.models import Accueilli
from flask_app.boucles_accueil.forms import AccueilliInfoForm

boucles_accueil = Blueprint('boucles_accueil', '__name__')


@boucles_accueil.route('/liste_accueillis')
@login_required
def liste_accueillis():
    accueillis = Accueilli.query.all()
    return render_template('liste_accueillis.html', accueillis=accueillis)


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
