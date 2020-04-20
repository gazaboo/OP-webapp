from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, logout_user, current_user, login_required

from flask_app import db, bcrypt

from flask_app.coordinateurs.forms import RegistrationForm, LoginForm
from flask_app.models import Coordinateur


coordinateurs = Blueprint("coordinateurs", '__name__')


@coordinateurs.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('accueillants.liste_accueillants'))
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
