from flask_app import app, db, bcrypt
import flask_app.utils_mailer as mailer
from flask_app.forms import SendMailForm, RegistrationForm, LoginForm
from flask import render_template, url_for, flash, redirect, request
from flask_app.models import Coordinateur, Accueillant, Email_OP
from collections import namedtuple
from flask_login import login_user, logout_user, current_user, login_required
from env import GOOGLE_APP_CREDS

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    # Get the data
    credentials = GOOGLE_APP_CREDS
    client = mailer.connect_to_drive(credentials)
    coordo_sheet = client.open("flask-Coordo/Mediation").worksheet("Accueillants")
    liste_accueillants_raw = coordo_sheet.get_all_values()
    Accueil = namedtuple('Accueil', ['dispo', 'nom', 'tel', 'adresse', 'prochaine_action', 'historique', 'dernier_mail_date', 'adresse_mail'])
    liste_accueillants = [Accueil(*row[:8]) for i,row in enumerate(liste_accueillants_raw) if i>1]

    # Send email
    form = SendMailForm()
    if form.validate_on_submit():
        mailer.send_email_simple('florian.dadouchi@gmail.com', form.body.data, 'test formulaire')

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
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
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
