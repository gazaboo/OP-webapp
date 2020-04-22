from flask_login import UserMixin
from datetime import datetime
from flask_app import db, login_manager
from sqlalchemy.orm import relationship, backref


@login_manager.user_loader
def load_coordinateur(coordo_id):
    return Coordinateur.query.get(int(coordo_id))


class Accueil(db.Model):
    __tablename__ = 'accueils'
    id = db.Column(db.Integer, primary_key=True)
    accueillant_id = db.Column(db.Integer, db.ForeignKey(
        'accueillants.id', ondelete="cascade"))
    accueilli_id = db.Column(db.Integer, db.ForeignKey(
        'accueillis.id', ondelete="cascade"))
    # dates_accueil = db.Column(ARRAY(db.Date))


class Accueillant(db.Model):
    __tablename__ = 'accueillants'
    id = db.Column(db.Integer, primary_key=True)
    disponibilite = db.Column(db.String(120), unique=False, nullable=True)
    nom = db.Column(db.String(120), unique=True, nullable=False)
    tel = db.Column(db.String(120), unique=False, nullable=True)
    adresse = db.Column(db.String(120), unique=False, nullable=True)
    email = db.Column(db.String(120), unique=False, nullable=True)
    next_action = db.Column(db.Text, unique=False, nullable=True)
    remarques = db.Column(db.Text, unique=False, nullable=True)
    accueillis = db.relationship("Accueilli",
                                 secondary='accueils',
                                 backref=db.backref('accueillants'))

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


class Accueilli(db.Model):
    __tablename__ = 'accueillis'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=True)
    tel = db.Column(db.String(120), unique=False, nullable=True)
    remarques = db.Column(db.Text, unique=False, nullable=True)

    def __init__(self, nom, email, tel, remarques):
        self.nom = nom
        self.email = email
        self.tel = tel
        self.remarques = remarques

    def __repr__(self):
        return f"Accueilli : {self.nom}, {self.email}"


class Email_OP(db.Model):
    __tablename__ = 'emails_op'
    id = db.Column(db.Integer, primary_key=True)
    from_ = db.Column(db.String(120), nullable=False)
    to_ = db.Column(db.String(120), nullable=False)
    date_ = db.Column(db.DateTime, nullable=False, unique=True)
    subject_ = db.Column(db.String(120), nullable=False)
    body_ = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Mail : {self.from_}, {self.subject_}"

    def __init__(self, from_, to_, date_, subject_, body_):
        self.from_ = from_
        self.to_ = to_
        self.date_ = date_
        self.subject_ = subject_
        self.body_ = body_


# class Accueil(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     accueillant_id = db.Column(db.Integer, db.ForeignKey('accueillant.id'))
#     accueilli_id = db.Column(db.Integer, db.ForeignKey('accueilli.id'))

#     accueillant = relationship(Accueillant, backref=backref("accueil", cascade="all, delete-orphan"))
#     accueilli = relationship(Accueilli, backref=backref("accueil", cascade="all, delete-orphan"))

#     def __init__(self, from_, to_, date_, subject_, body_):
#         self.accueillant_id = accueillant_id
#         self.accueilli_id = accueilli_id


# Accueil = db.Table('accueils',
#                    db.Column('id',
#                              db.Integer,
#                              primary_key=True),
#                    db.Column('accueillant_id',
#                              db.Integer,
#                              db.ForeignKey('accueillants.id', ondelete="cascade")),
#                    db.Column('accueilli_id',
#                              db.Integer,
#                              db.ForeignKey('accueillis.id', ondelete="cascade")))
