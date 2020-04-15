from flask_app import app, db, bcrypt
import flask_app.utils_mailer as mailer
from flask_app.forms import SendMailForm, RegistrationForm, LoginForm, AccueillantInfoForm
from flask import render_template, url_for, flash, redirect, request
from flask_app.models import Coordinateur, Accueillant, Email_OP
from collections import namedtuple
from flask_login import login_user, logout_user, current_user, login_required
from env import GOOGLE_APP_CREDS
from flask_app.utils_mailer import get_mail_from_last, get_conversations


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    liste_accueillants = Accueillant.query.all()

    # Send email
    form = SendMailForm()
    if form.validate_on_submit():
        mailer.send_email_simple(
            'florian.dadouchi@gmail.com', form.body.data, 'test formulaire')

    return render_template('home.html', accueillants=liste_accueillants, title="Accueillants", form=form)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        coordo = Coordinateur.query.filter_by(email=form.email.data).first()
        if coordo and bcrypt.check_password_hash(coordo.password, form.password.data):
            login_user(coordo, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
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
        return redirect(url_for('home'))
    return render_template('accueillant_infos.html',
                           title='create_modif_accueillant',
                           legend='Nouvel Accueillant',
                           form=form,
                           accueillant=None)


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
        return redirect(url_for('home'))
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
    return redirect(url_for('home'))


@app.route('/synchronize', methods=['GET', 'POST'])
@login_required
def synchronize():
    # Get the data
    credentials = GOOGLE_APP_CREDS
    client = mailer.connect_to_drive(credentials)
    coordo_sheet = client.open(
        "flask-Coordo/Mediation").worksheet("Accueillants")
    liste_accueillants_raw = coordo_sheet.get_all_values()
    liste_accueillants_to_add = [Accueillant(
        *row[:7]) for i, row in enumerate(liste_accueillants_raw) if i > 1]

    for acc in liste_accueillants_to_add:
        try:
            db.session.add(acc)
            db.session.commit()
        except:
            db.session.close()

    form = SendMailForm()
    liste_accueillants = Accueillant.query.all()
    return render_template('home.html', accueillants=liste_accueillants, title="Accueillants", form=form)


@app.route('/synchronize_email', methods=['GET', 'POST'])
@login_required
def synchronize_email():
    mails_roundcube = get_mail_from_last(5)
    mail_dict = get_conversations(mails_roundcube)
    print(mail_dict)
    return render_template('index.html', mails=mail_dict, title="Index")
