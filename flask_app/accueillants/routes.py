import re

from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_required
from flask_mail import Message
from bs4 import BeautifulSoup as soup

from env import GOOGLE_APP_CREDS
from flask_app import db, mail
from flask_app.models import Accueillant, Email_OP, Accueilli
from flask_app.accueillants.forms import SendMailForm, AccueillantInfoForm
from flask_app.accueillants.utils_mailer import get_mail_from_last, get_conversations, send_email_simple, connect_to_drive


accueillants = Blueprint('accueillants', '__name__')


@accueillants.route('/liste_accueillants')
@login_required
def liste_accueillants():
    liste_accueillants = Accueillant.query.all()
    dict_emails = get_conversations(Email_OP.query.distinct())
    return render_template('liste_accueillants.html',
                           accueillants=liste_accueillants,
                           emails=dict_emails,
                           title="Accueillants")


@accueillants.route('/email_accueillant/<int:acc_id>', methods=['GET', 'POST'])
@login_required
def email_accueillant(acc_id):
    acc = Accueillant.query.get_or_404(acc_id)
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
        return redirect(url_for('accueillants.liste_accueillants')+f"#{acc.id}")
    elif request.method == 'GET':
        form.destinataire.data = acc.email
    return render_template('email_accueillant.html',
                           accueillant=acc,
                           emails=dict_emails,
                           title="Accueillants",
                           form=form)


@accueillants.route('/accueillant/new', methods=['GET', 'POST'])
@login_required
def new_accueillant():
    form = AccueillantInfoForm()
    accueillis = Accueilli.query.all()

    if form.validate_on_submit():
        accueillant = Accueillant(disponibilite=form.disponibilite.data,
                                  nom=form.nom.data,
                                  tel=form.tel.data,
                                  adresse=form.adresse.data,
                                  email=form.email.data,
                                  next_action=form.next_action.data,
                                  remarques=form.remarques.data)

        values = request.form.getlist('check')
        list_acc = [Accueilli.query.get(v) for v in values]
        accueillant.accueillis.extend(list_acc)
        db.session.add(accueillant)
        db.session.commit()
        flash('Accueillant créé', 'success')
        return redirect(url_for('accueillants.liste_accueillants'))
    return render_template('accueillant_infos.html',
                           title='create_modif_accueillant',
                           legend='Nouvel Accueillant',
                           form=form,
                           accueillant=None,
                           accueillis=accueillis)


@accueillants.route('/accueillant/<int:acc_id>', methods=['GET', 'POST'])
@login_required
def update_accueillant(acc_id):
    acc = Accueillant.query.get_or_404(acc_id)
    form = AccueillantInfoForm()
    accueillis = Accueilli.query.all()

    if form.validate_on_submit():
        acc.nom = form.nom.data
        acc.tel = form.tel.data
        acc.adresse = form.adresse.data
        acc.email = form.email.data
        acc.next_action = form.next_action.data
        acc.remarques = form.remarques.data
        values = request.form.getlist('check')
        list_acc = [Accueilli.query.get(v) for v in values]
        acc.accueillis = list_acc
        db.session.commit()
        return redirect(url_for('accueillants.liste_accueillants')+f"#{acc.id}")
    elif request.method == 'GET':
        form.nom.data = acc.nom
        form.tel.data = acc.tel
        form.adresse.data = acc.adresse
        form.email.data = acc.email
        form.next_action.data = acc.next_action
        form.remarques.data = acc.remarques
        list_to_check = [a.id for a in acc.accueillis]

    return render_template('accueillant_infos.html',
                           title='create_modif_accueillant',
                           legend='Modifier les Infos',
                           form=form,
                           accueillant=acc,
                           accueillis=accueillis,
                           list_to_check=list_to_check)


@accueillants.route('/accueillant/<int:acc_id>/delete', methods=['POST'])
@login_required
def delete_accueillant(acc_id):
    acc = Accueillant.query.get_or_404(acc_id)
    db.session.delete(acc)
    db.session.commit()
    flash(f'Accueillant "{acc.nom}" enlevé de la liste', 'success')
    return redirect(url_for('accueillants.liste_accueillants'))


#######################
# Pour la mise en route
#######################

@accueillants.route('/synchronize', methods=['GET', 'POST'])
@login_required
def synchronize():
    # Get the data
    credentials = GOOGLE_APP_CREDS
    client = connect_to_drive(credentials)
    coordo_sheet = client.open(
        "flask-Coordo/Mediation").worksheet("Accueillants")
    liste_accueillants_raw = coordo_sheet.get_all_values()

    # Handle poorly formatted emails
    emails_re = "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    tel_re = "([0-9][0-9])"
    liste_accueillants_to_add = \
        [Accueillant(
            disponibilite=row[0],
            nom=row[1].title(),
            tel=''.join("; " if i % 15 == 0 else char for i, char in enumerate(
                ".".join(re.findall(tel_re, row[2])), 1)),
            adresse=row[3],
            email="; ".join(re.findall(emails_re, row[4])).lower(),
            next_action=row[5],
            remarques=row[6])
            for i, row in enumerate(liste_accueillants_raw) if i > 1]

    for acc in liste_accueillants_to_add:
        try:
            db.session.add(acc)
            db.session.commit()
        except:
            db.session.close()

    return redirect(url_for('accueillants.liste_accueillants'))


@accueillants.route('/synchronize_email')
@login_required
def synchronize_email():
    mails_roundcube = get_mail_from_last(180)

    for m in mails_roundcube:
        # Remove the replies
        dom = soup(m.body_, 'html.parser')
        quote = dom.find_all("div", class_="gmail_quote") \
            + dom.findAll('blockquote')  \
            + dom.findAll("div", class_='yahoo_quoted')  \
            + dom.findAll("div", class_='x_gmail_quote') \
            + dom.findAll('div', attrs={"data-marker": "__QUOTED_TEXT__"}) \
            + dom.findAll('div', attrs={"data-marker": "__HEADERS__"}) \
            + dom.findAll('div', attrs={"data-marker": "__SIG_PRE__"})

        for tag in quote:
            try:
                tag.decompose()
            except:
                pass

        # Update body
        m.body_ = str(dom)

    mail_dict = get_conversations(mails_roundcube)
    for liste_emails in mail_dict.values():
        for mail in liste_emails:
            try:
                db.session.add(mail)
                db.session.commit()
            except:
                db.session.close()

    return render_template('index.html', mails=mail_dict, title="Index")
