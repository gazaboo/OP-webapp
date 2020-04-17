from flask_login import UserMixin
from datetime import datetime
from flask_app import db, login_manager


@login_manager.user_loader
def load_coordinateur(coordo_id):
    return Coordinateur.query.get(int(coordo_id))


class Accueillant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disponibilite = db.Column(db.String(120), unique=False, nullable=True)
    nom = db.Column(db.String(120), unique=True, nullable=False)
    tel = db.Column(db.String(120), unique=False, nullable=True)
    adresse = db.Column(db.String(120), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=False, nullable=True)
    next_action = db.Column(db.Text, unique=False, nullable=True)
    remarques = db.Column(db.Text, unique=False, nullable=True)

    def __repr__(self):
        return f"Accueillant : {self.nom}, {self.email}"

    def __init__(self, disponibilite, nom, tel, adresse, email, next_action, remarques):
        self.disponibilite = disponibilite
        self.nom = nom
        self.tel = tel
        self.adresse = adresse
        self.email = email
        self.next_action = next_action
        self.remarques = remarques


class Coordinateur(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=True,
                           default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Coordo : {self.nom}, {self.email}"


class Email_OP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_ = db.Column(db.String(120), nullable=False)
    to_ = db.Column(db.String(120), nullable=False)
    date_ = db.Column(db.DateTime, nullable=False, unique=True)
    subject_ = db.Column(db.String(120), nullable=False)
    body_ = db.Column(db.Text, nullable=False)
    # acc_id_ = db.Column(db.Integer, db.ForeignKey(
    #     'accueillant.id'), nullable=True)

    def __repr__(self):
        return f"Mail : {self.from_}, {self.subject_}"

    # def set_accueillant(acc_id):
    #     self.acc_id_ = acc_id

    def __init__(self, from_, to_, date_, subject_, body_):
        self.from_ = from_
        self.to_ = to_
        self.date_ = date_
        self.subject_ = subject_
        self.body_ = body_
        # self.acc_id_ = acc_id_
