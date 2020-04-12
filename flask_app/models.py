from datetime import datetime
from flask_app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_coordinateur(coordo_id):
    return Coordinateur.query.get(int(coordo_id))

class Accueillant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    historique_msg = db.relationship('Email_OP', backref='author', lazy=True)

    def __repr__(self):
        return f"Accueillant : {self.nom}, {self.email}"

class Coordinateur(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Coordo : {self.nom}, {self.email}"

class Email_OP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_ = db.Column(db.String(120), nullable=False)
    object_ = db.Column(db.String(120), nullable=False)
    body_ = db.Column(db.Text, nullable=False)
    date_ = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('accueillant.id'), nullable=False)

    def __repr__(self):
        return f"Mail : {self.from_}, {self.object_}"
 