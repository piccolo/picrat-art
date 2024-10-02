import streamlit as st
import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3

# Configuration pour l'envoi d'emails
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "vincent.roullier@gmail.com"
SMTP_PASSWORD = "hhxg qzst jemv hvxt"

# Initialisation de la base de données
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (email TEXT PRIMARY KEY, link_id TEXT, is_active INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activities
                 (id INTEGER PRIMARY KEY, email TEXT, niveau TEXT, sous_niveau TEXT, 
                 frequence TEXT, score INTEGER)''')
    conn.commit()
    conn.close()

# Fonction pour ajouter ou mettre à jour un utilisateur
def upsert_user(email, link_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (email, link_id, is_active) VALUES (?, ?, 1)",
              (email, link_id))
    conn.commit()
    conn.close()

# Fonction pour vérifier si un lien est valide
def is_valid_link(link_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT email FROM users WHERE link_id = ? AND is_active = 1", (link_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def send_login_link(email):
    unique_id = str(uuid.uuid4())
    login_link = f"http://localhost:8501/?id={unique_id}"
    
    upsert_user(email, unique_id)

    message = MIMEMultipart()
    message["From"] = SMTP_USERNAME
    message["To"] = email
    message["Subject"] = "Votre lien de connexion"
    body = f"Voici votre lien de connexion unique : {login_link}"
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(message)

def save_activity(email, niveau, sous_niveau, frequence, score):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''INSERT INTO activities 
                 (email, niveau, sous_niveau, frequence, score) 
                 VALUES (?, ?, ?, ?, ?)''', 
              (email, niveau, sous_niveau, frequence, score))
    conn.commit()
    conn.close()

def activity_form(email):
    st.header("Enregistrement d'une activité")
    
    niveau = st.selectbox("Niveau", ["Collège", "Lycée", "Post-Bac"])
    
    sous_niveau = ""
    if niveau == "Collège":
        sous_niveau = st.selectbox("Classe", ["6e", "5e", "4e", "3e"])
    elif niveau == "Lycée":
        sous_niveau = st.selectbox("Classe", ["Seconde", "Première", "Terminale"])
    
    frequence = st.selectbox("Fréquence de l'activité", 
                             ["Très souvent (plusieurs fois par semaine)", 
                              "Souvent (Une fois par semaine)", 
                              "Parfois (1 fois par mois)", 
                              "Rarement (quelques fois dans l'année)"])
    
    st.subheader("Questions PIC-RAT")

    resultat = 0
    interaction = st.radio("Est-ce que la technologie permet aux élèves d'interagir ?",("Oui", "Non"), index=None)
    if interaction == 'Oui':
        resultat  = 1
        construction = st.radio("Est-ce que la technologie permet à l'élève de participer à la construction de sa connaissance ?",("Oui", "Non"),index=None)
        if construction == 'Oui':
            resultat = 2
    
    analogique = st.radio("Est-ce que cette activité peut être réalisée de manière identique en analogique ?",("Oui", "Non"),index=None)
    if analogique == 'Oui':
        resultat = resultat + 10
        transformation = st.radio("Est-ce que la technologie transforme les tâches d'apprentissage ?",("Oui", "Non"),index=None)
        if transformation == 'Oui':
            resultat = resultat + 10
    
    if st.button("Enregistrer l'activité"):
        save_activity(email, niveau, sous_niveau, frequence, resultat) 
        st.success("Activité enregistrée avec succès!")

def main():
    st.title("Enregistrement d'activités pédagogiques")

    init_db()

    params = st.experimental_get_query_params()
    unique_id = params.get("id", [""])[0]

    if unique_id:
        email = is_valid_link(unique_id)
        if email:
            st.success(f"Connecté en tant que {email}")
            activity_form(email)
        else:
            st.error("Lien de connexion invalide ou expiré.")
            st.button("Retour à l'inscription", on_click=lambda: st.experimental_set_query_params())
    else:
        st.header("Inscription / Connexion")
        email = st.text_input("Adresse email")
        if st.button("Envoyer le lien de connexion"):
            try:
                send_login_link(email)
                st.success("Un lien de connexion a été envoyé à votre adresse email.")
                st.write("Veuillez vérifier votre boîte de réception et cliquer sur le lien pour vous connecter.")
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de l'envoi de l'email : {str(e)}")

if __name__ == "__main__":
    main()