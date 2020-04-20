
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

from env import APP_CONFIG_SECRET_KEY

app = Flask(__name__)
app.config['SECRET_KEY'] = APP_CONFIG_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
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
