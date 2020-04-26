from flask import (render_template, url_for, flash,
                   redirect, request, Blueprint)
from flask_login import (login_user, logout_user,
                         current_user, login_required)
from flask_app import db, bcrypt
from flask_app.coordinateurs.utils import send_email_invitation, send_reset_email
from flask_app.coordinateurs.forms import (RegistrationForm, LoginForm, AddCoordoForm,
                                           RequestResetPassword, ResetPasswordForm)
from flask_app.models import Coordinateur
import random
import datetime as dt


coordinateurs = Blueprint("coordinateurs", '__name__')


@coordinateurs.route('/add_coordo', methods=['GET', 'POST'])
@login_required
def add_coordo():
    form = AddCoordoForm()
    if form.validate_on_submit():
        password = "".join(random.sample(
            'abcdefghijklmnoparstuvwxyz_./:#{[123456789', 12))
        nom = dt.datetime.now().strftime('%f')
        hashed_password = bcrypt.generate_password_hash(
            password).decode('utf-8')
        coordo = Coordinateur(nom="NewCoordo-"+nom,
                              email=form.email.data,
                              password=hashed_password)
        db.session.add(coordo)
        db.session.commit()
        send_email_invitation(coordo)
        flash(f"Email d'invitation envoyé à {form.email.data}", 'info')
        return redirect(url_for('accueillants.liste_accueillants'))
    return render_template('add_coordo.html', title='Ajouter un coordinateur', form=form)


@coordinateurs.route('/register/<token>', methods=['GET', 'POST'])
def register(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    coordo = Coordinateur.verify_reset_token(token)
    if coordo is None:
        flash('Lien invalide ou expiré', 'warning')
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    form.email.data = coordo.email
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        coordo.password = hashed_password
        coordo.nom = form.username.data
        db.session.commit()
        flash(f'Compte créé pour {form.username.data} !', 'success')
        return redirect(url_for('coordinateurs.login'))
    return render_template('register.html', title='Register', form=form)


@coordinateurs.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('accueillants.liste_accueillants'))
    form = LoginForm()
    if form.validate_on_submit():
        coordo = Coordinateur.query.filter_by(email=form.email.data).first()
        if coordo and bcrypt.check_password_hash(coordo.password, form.password.data):
            login_user(coordo, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('accueillants.liste_accueillants'))
        else:
            flash('Login Unsuccessfull, check email and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@coordinateurs.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@coordinateurs.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('accueillants.liste_accueillants'))
    form = RequestResetPassword()
    if form.validate_on_submit():
        coordo = Coordinateur.query.filter_by(email=form.email.data).first()
        send_reset_email(coordo)
        flash('Email envoyé pour réinitialisation', 'info')
        return redirect(url_for('coordinateurs.login'))
    return render_template('reset_request.html', title='Demander un changement de mot de passe', form=form)


@coordinateurs.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('accueillants.liste_accueillants'))

    coordo = Coordinateur.verify_reset_token(token)
    if coordo is None:
        flash('Lien invalide ou expiré', 'warning')
        return redirect(url_for('coordinateurs.reset_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        coordo.password = hashed_password
        db.session.commit()
        flash(f'Votre mot de passe a été modifié.', 'success')
        return redirect(url_for('coordinateurs.login'))
    return render_template('reset_token.html', title='Changement de mot de passe', form=form)
