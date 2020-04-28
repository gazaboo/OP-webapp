from flask.cli import FlaskGroup
from flask_app import app, db, bcrypt
from flask_app.models import Accueillant, Coordinateur
from env import GOOGLE_APP_CREDS, PASS_ADMIN
from flask_app.accueillants.utils_mailer import connect_to_drive
import re


cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()

    # Add the admin
    hashed_password = bcrypt.generate_password_hash(PASS_ADMIN).decode('utf-8')
    coordo = Coordinateur(
        nom="admin", email="admin@admin.org", password=hashed_password)
    db.session.add(coordo)
    db.session.commit()

    # Get the data
    credentials = GOOGLE_APP_CREDS
    client = connect_to_drive(credentials)
    coordo_sheet = client.open(
        "flask-Coordo/Mediation").worksheet("Accueillants")
    liste_accueillants_raw = coordo_sheet.get_all_values()

    # Handle poorly formatted emails
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


if __name__ == "__main__":
    cli()
