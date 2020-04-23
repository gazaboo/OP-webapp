
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from env import APP_CONFIG_SECRET_KEY, LOP_PASS, LOP_LOGIN, LOP_HOST

mail_settings = {
    "MAIL_SERVER": LOP_HOST,
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": LOP_LOGIN,
    "MAIL_PASSWORD": LOP_PASS,
    "MAIL_DEFAULT_SENDER": LOP_LOGIN
}

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_CONFIG_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config.update(mail_settings)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)
login_manager.login_view = 'coordinateurs.login'
login_manager.login_message_category = 'info'

from flask_app.main.routes import main
from flask_app.boucles_accueil.routes import boucles_accueil
from flask_app.coordinateurs.routes import coordinateurs
from flask_app.accueillants.routes import accueillants

app.register_blueprint(main)
app.register_blueprint(boucles_accueil)
app.register_blueprint(coordinateurs)
app.register_blueprint(accueillants)

# from flask_datepicker import datepicker
# from flask_bootstrap import Bootstrap

# datepicker(app)