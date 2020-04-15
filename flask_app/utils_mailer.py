import datetime as dt
from imap_tools import MailBox, Q, OR
from imap_tools.imap_utf7 import decode
import imaplib
from datetime import datetime
import smtplib
from email.message import EmailMessage
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from collections import namedtuple

from env import LOP_PASS, LOP_LOGIN, LOP_HOST


def updateDB(sheet):
    sheet_values_raw = sheet.get_all_values()


def get_planning(sheet):
    ######################################
    # Process the data
    begin_row = 0
    for i, val in enumerate(sheet.get_all_values()):
        if any(list(map(lambda x: 'ACCUEIL' in x, val))):
            begin_row = i+1
            break

    mail_content_all_cols = sheet.get_all_values()[begin_row:]
    mail_content = [x[:3] for x in mail_content_all_cols]

    html = "<table class=mystyle>"
    html += "<tr>"
    html += "\n".join(map(lambda x: "<th>" + x + "</th>", mail_content[0]))
    html += "<tr>"
    for row in mail_content[1:]:
        html += "<tr>"
        # Make <tr>-pairs, then join them.
        html += "\n".join(map(lambda x: "<td>" + x + "</td>", row))
        html += "</tr>"
    html += "</table>"

    return html


def send_email(info_accueil, html, email_info):
    import os
    # email_host = os.getenv('EMAIL_HOST')

    print(
        f'[Ouvre-Porte] Mediation {info_accueil.Accueilli} - Mail automatique')
    ######################################
    # Send the email
    msg = EmailMessage()
    msg['Subject'] = f'[Ouvre-Porte] Mediation {info_accueil.Accueilli} - Mail automatique'
    msg['From'] = email_info.login
    msg['To'] = info_accueil.Mail_mediateur

    msg.add_alternative(html, subtype='html')

    with smtplib.SMTP_SSL(email_info.host, 465) as smtp:
        # PASSWORD = os.getenv('LOP_PASS')
        smtp.login(email_info.login, email_info.password)
        smtp.send_message(msg)


def generate_logs(log_sheet, infos):
    # Log for debugging purposes
    now = datetime.today()
    now = now.strftime("%d-%m-%Y")
    log_sheet.append_row([now.__str__(), infos.Mediateur],
                         value_input_option='RAW')


def connect_to_drive(creds_raw):
    import json
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file",
             "https://www.googleapis.com/auth/drive"]

    creds_json = json.loads(creds_raw)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    return client


def send_email_simple(to_, body_, object_):
    import smtplib
    from email.message import EmailMessage

    msg = EmailMessage()
    msg['Subject'] = object_
    msg['From'] = LOP_LOGIN
    msg['To'] = to_
    html = f'<html> <body> {body_} </body></html>'
    msg.add_alternative(html, subtype='html')

    with smtplib.SMTP_SSL(LOP_HOST, 465) as smtp:
        smtp.login(LOP_LOGIN, LOP_PASS)
        smtp.send_message(msg)


def get_mailbox_folders():
    LOP_PASS = 'LOP2018!'
    LOP_LOGIN = 'grenoble@louvreporte.org'
    LOP_HOST = 'mail.gandi.net'
    imap = imaplib.IMAP4_SSL(LOP_HOST)
    imap.login(LOP_LOGIN, LOP_PASS)

    # Get the folders
    raw_folders = [decode(folder) for folder in imap.list()[1]]
    folders = [folder.split(' "/" ')[1].replace('"', '')
               for folder in raw_folders]
    return folders


def get_mail_from_last(num_days):
    folders = get_mailbox_folders()
    mails_roundcube = []
    with MailBox(LOP_HOST).login(LOP_LOGIN, LOP_PASS) as mailbox:
        for folder in folders:
            mailbox.folder.set(folder)
            mails = mailbox.fetch(
                Q(date_gte=dt.date.today() - dt.timedelta(days=num_days)))
            for mail in mails:
                try:
                    query_result = EmailOP(
                        mail.from_, mail.to, mail.date, mail.subject, mail.html)
                    mails_roundcube = mails_roundcube + [query_result]
                except Exception as e:
                    print(e)
                    print('erreur :', mail.from_, " date : ", mail.date)
    return mails_roundcube


def get_conversations(mails_roundcube):
    liste_receivers_deep = [mail.to_ for mail in mails_roundcube]

    liste_receivers_flat = [
        receiver for tuple_ in liste_receivers_deep for receiver in tuple_]

    liste_emails = [mail.from_ for mail in mails_roundcube] + \
        liste_receivers_flat

    mail_Dict = {k: [mail for mail in mails_roundcube if (mail.from_ == k or k in mail.to_)]
                 for k in set(liste_emails)}

    mail_Dict_sorted = {k: sorted(v, key=lambda x: x.date_, reverse=True)
                        for k, v in mail_Dict.items()}

    return mail_Dict_sorted
