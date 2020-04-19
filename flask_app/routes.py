from flask_app import app, db, bcrypt
import flask_app.utils_mailer as mailer
from flask_app.forms import SendMailForm, RegistrationForm, LoginForm, AccueillantInfoForm, AccueilliInfoForm
from flask import render_template, url_for, flash, redirect, request
from flask_app.models import Coordinateur, Accueillant, Email_OP, Accueilli
from collections import namedtuple
from flask_login import login_user, logout_user, current_user, login_required
from env import GOOGLE_APP_CREDS
from flask_app.utils_mailer import get_mail_from_last, get_conversations


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/liste_accueillis')
def liste_accueillis():
    accueillis = Accueilli.query.all()
    return render_template('test.html', accueillis=accueillis)


@app.route('/liste_accueillants', methods=['GET', 'POST'])
@login_required
def liste_accueillants():
    liste_accueillants = Accueillant.query.all()
    dict_emails = get_conversations(Email_OP.query.distinct())

    # Send email
    form = SendMailForm()
    if form.validate_on_submit():
        mailer.send_email_simple(
            'florian.dadouchi@gmail.com', form.body.data, 'test formulaire')

    return render_template('liste_accueillants.html',
                           accueillants=liste_accueillants,
                           emails=dict_emails,
                           title="Accueillants",
                           form=form)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('liste_accueillants'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        coordo = Coordinateur(nom=form.username.data,
                              email=form.email.data,
                              password=hashed_password)
        db.session.add(coordo)
        db.session.commit()
        flash(f'Account created for {form.username.data} !', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('liste_accueillants'))
    form = LoginForm()
    if form.validate_on_submit():
        coordo = Coordinateur.query.filter_by(email=form.email.data).first()
        if coordo and bcrypt.check_password_hash(coordo.password, form.password.data):
            login_user(coordo, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('liste_accueillants'))
        else:
            flash('Login Unsuccessfull, check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/accueillant/new', methods=['GET', 'POST'])
@login_required
def new_accueillant():
    form = AccueillantInfoForm()
    if form.validate_on_submit():
        accueillant = Accueillant(disponibilite=form.disponibilite.data,
                                  nom=form.nom.data,
                                  tel=form.tel.data,
                                  adresse=form.adresse.data,
                                  email=form.email.data,
                                  next_action=form.next_action.data,
                                  remarques=form.remarques.data)
        db.session.add(accueillant)
        db.session.commit()
        flash('Accueillant créé', 'success')
        return redirect(url_for('liste_accueillants'))
    return render_template('accueillant_infos.html',
                           title='create_modif_accueillant',
                           legend='Nouvel Accueillant',
                           form=form,
                           accueillant=None)

@app.route('/accueilli/new', methods=['GET', 'POST'])
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
        return redirect(url_for('liste_accueillis'))
    return render_template('accueilli_infos.html',
                           title='create_modif_accueillant',
                           legend='Nouvel Accueillant',
                           form=form)

@app.route('/accueillant/<int:acc_id>', methods=['GET', 'POST'])
@login_required
def update_accueillant(acc_id):
    acc = Accueillant.query.get_or_404(acc_id)
    form = AccueillantInfoForm()

    if form.validate_on_submit():
        acc.nom = form.nom.data
        acc.tel = form.tel.data
        acc.adresse = form.adresse.data
        acc.email = form.email.data
        acc.next_action = form.next_action.data
        acc.remarques = form.remarques.data
        db.session.commit()
        return redirect(url_for('liste_accueillants'))
    elif request.method == 'GET':
        form.nom.data = acc.nom
        form.tel.data = acc.tel
        form.adresse.data = acc.adresse
        form.email.data = acc.email
        form.next_action.data = acc.next_action
        form.remarques.data = acc.remarques

    return render_template('accueillant_infos.html',
                           title='create_modif_accueillant',
                           legend='Modifier les Infos',
                           form=form,
                           accueillant=acc)


@app.route('/accueillant/<int:acc_id>/delete', methods=['POST'])
@login_required
def delete_accueillant(acc_id):
    acc = Accueillant.query.get_or_404(acc_id)
    db.session.delete(acc)
    db.session.commit()
    flash(f'Accueillant "{acc.nom}" enlevé de la liste', 'success')
    return redirect(url_for('liste_accueillants'))


#######################
# Pour la mise en route
#######################

@app.route('/synchronize', methods=['GET', 'POST'])
@login_required
def synchronize():
    # Get the data
    credentials = GOOGLE_APP_CREDS
    client = mailer.connect_to_drive(credentials)
    coordo_sheet = client.open(
        "flask-Coordo/Mediation").worksheet("Accueillants")
    liste_accueillants_raw = coordo_sheet.get_all_values()

    # Handle poorly formatted emails
    import re
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

    return redirect(url_for('liste_accueillants'))


@app.route('/synchronize_email')
@login_required
def synchronize_email():
    from bs4 import BeautifulSoup as soup
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
