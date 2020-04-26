from flask import render_template, url_for, flash, redirect, Blueprint
from flask_login import login_required
from flask_app import db
from flask_app.models import Accueilli, Accueillant, Email_OP, Sejour
from flask_app.boucles_accueil.forms import AccueilliInfoForm, NewAccueilForm
from flask_app.accueillants.utils_mailer import get_conversations
from flask_app.accueillants.forms import SendMailForm
from sqlalchemy import desc

boucles_accueil = Blueprint('boucles_accueil', '__name__')


@boucles_accueil.route('/boucle/<int:acc_id>', methods=['GET', 'POST'])
@login_required
def boucle(acc_id):
    accueilli = Accueilli.query.get_or_404(acc_id)
    sejours = (Sejour.query.filter_by(accueilli_id=accueilli.id)
                           .order_by(desc("date_debut"))
                           .all())

    dict_emails = get_conversations(Email_OP.query.distinct())
    liste_accueillants = Accueillant.query.filter(
        Accueillant.id.in_([a.id for a in accueilli.accueillants])).all()
    form = NewAccueilForm(obj=accueilli)
    form.accueillant.choices = [(acc.id, acc.nom)
                                for acc in liste_accueillants]
    if form.validate_on_submit():
        new_sejour = Sejour(accueilli_id=accueilli.id,
                            accueillant_id=form.accueillant.data,
                            date_debut=form.date_debut.data,
                            date_fin=form.date_fin.data,
                            remarque=form.remarque.data)
        db.session.add(new_sejour)
        db.session.commit()
        return redirect(url_for('boucles_accueil.boucle', acc_id=accueilli.id))
    return render_template('boucle.html',
                           accueilli=accueilli,
                           form=form,
                           emails=dict_emails,
                           sejours=sejours)


@boucles_accueil.route('/liste_boucles')
@login_required
def liste_boucles():
    accueillis = Accueilli.query.all()
    liste_accueillants = Accueillant.query.all()
    return render_template('liste_boucles.html', accueillis=accueillis,
                           accueillants=liste_accueillants)


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
        return redirect(url_for('boucles_accueil.liste_boucles'))
    return render_template('accueilli_infos.html',
                           title='create_modif_accueilli',
                           legend='Nouvel Accueilli',
                           form=form)


@boucles_accueil.route('/accueilli/update', methods=['GET', 'POST'])
@login_required
def update_accueilli():
    # form = AccueilliInfoForm()
    # if form.validate_on_submit():
    #     accueilli = Accueilli(nom=form.nom.data,
    #                           email=form.email.data,
    #                           tel=form.tel.data,
    #                           remarques=form.remarques.data)
    #     db.session.add(accueilli)
    #     db.session.commit()
    #     flash(f'Accueilli créé : {accueilli.nom}', 'success')
    #     return redirect(url_for('boucles_accueil.liste_accueillis'))
    return render_template('liste_boucles.html',
                           title='modif_accueilli',
                           legend='Update Accueilli')


@boucles_accueil.route('/email_accueilli/<int:acc_id>', methods=['GET', 'POST'])
@login_required
def email_accueilli(acc_id):
    acc = Accueilli.query.get_or_404(acc_id)
    dict_emails = get_conversations(Email_OP.query.distinct())
    form = SendMailForm()
    if form.validate_on_submit():
        emails_re = "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
        recipients = re.findall(emails_re, "florian.dadouchi@gmail.com")
        recipients = list(map(str.lower, recipients))
        cc = re.findall(emails_re, form.destinataire_copie.data)
        cc = list(map(str.lower, cc))
        msg = Message(subject=form.object_.data,
                      body=form.body.data,
                      recipients=recipients,
                      cc=cc)
        mail.send(msg)
        return redirect(url_for('boucles_accueil.liste_boucles')+f"#{acc.id}")
    elif request.method == 'GET':
        form.destinataire.data = acc.email
    return render_template('email_accueillant.html',
                           accueillant=acc,
                           emails=dict_emails,
                           title="Accueillants",
                           form=form)
