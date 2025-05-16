import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config.config import SMTP_CONFIG, APP_CONFIG

def send_login_email(email, unique_id):
    login_link = f"{APP_CONFIG['BASE_URL']}/?id={unique_id}"
    
    message = MIMEMultipart()
    message["From"] = SMTP_CONFIG["USERNAME"]
    message["To"] = email
    message["Subject"] = "Votre lien de connexion"
    body = f"Voici votre lien de connexion unique : {login_link}"
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_CONFIG["SERVER"], SMTP_CONFIG["PORT"]) as server:
        server.starttls()
        server.login(SMTP_CONFIG["USERNAME"], SMTP_CONFIG["PASSWORD"])
        server.send_message(message)