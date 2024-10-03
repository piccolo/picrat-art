import streamlit as st
import pandas as pd
from hashlib import sha256
import uuid
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import plotly.express as px
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

# Fonction pour générer un lien unique
def generate_unique_link():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')[:22]

# Fonction pour hacher les mots de passe (pour l'admin)
def hash_password(password):
    return sha256(password.encode()).hexdigest()

# Initialisation des données
@st.cache_resource
def init_data():
    users = pd.DataFrame({
        'username': ['admin', 'user1', 'user2'],
        'password': [hash_password('admin123'), '', ''],
        'is_admin': [True, False, False],
        'unique_link': ['', generate_unique_link(), generate_unique_link()],
        'last_login': [pd.Timestamp.now(), pd.Timestamp.now() - pd.Timedelta(days=2), pd.Timestamp.now() - pd.Timedelta(days=5)]
    })
    return users, {}

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

# Fonction d'authentification
def authenticate(username, password):
    user = st.session_state.users[st.session_state.users['username'] == username]
    if not user.empty and user.iloc[0]['is_admin']:
        if user.iloc[0]['password'] == hash_password(password):
            return True
    return False

# Page principale
def main():
    st.title("Application avec authentification par lien unique")
    
    if 'users' not in st.session_state or 'active_links' not in st.session_state:
        st.session_state.users, st.session_state.active_links = init_data()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Vérification du lien unique dans l'URL
    params = st.experimental_get_query_params()
    unique_id = params.get("id",[""])[0]
    if unique_id:
        st.write("unique id {unique_id}")        
        email = is_valid_link(unique_id)
        st.write("unique id {unique_id}")        
        if email:
            st.success(f"Connecté en tant que {email}")
            st.session_state.logged_in = True
            st.session_state.is_admin = False
            st.session_state.username = email
            #user_index = st.session_state.users.index[st.session_state.users['unique_link'] == link].tolist()[0]
            #st.session_state.users.at[user_index, 'last_login'] = pd.Timestamp.now()
            st.experimental_set_query_params()
            st.rerun()
    # if 'link' in params:
    #     link = params['link'][0]
    #     user = st.session_state.users[st.session_state.users['unique_link'] == link]
    #     if not user.empty:
    #         st.session_state.logged_in = True
    #         st.session_state.is_admin = user.iloc[0]['is_admin']
    #         st.session_state.username = user.iloc[0]['username']
    #         user_index = st.session_state.users.index[st.session_state.users['unique_link'] == link].tolist()[0]
    #         st.session_state.users.at[user_index, 'last_login'] = pd.Timestamp.now()
    #         st.experimental_set_query_params()
    #         st.rerun()
    
    if not st.session_state.logged_in:
        username = st.text_input("Nom d'utilisateur (admin)")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Authentification échouée")
    else:
        if st.sidebar.button("Se déconnecter"):
            st.session_state.logged_in = False
            st.rerun()
        
        if st.session_state.is_admin:
            admin_pages()
        else:
            user_pages()

def admin_pages():
    st.sidebar.title(f"Bienvenue, {st.session_state.username}")
    
    pages = {
        "Tableau de bord": dashboard_page,
        "Gestion des utilisateurs": user_management_page,
        "Paramètres": settings_page
    }
    
    selection = st.sidebar.radio("Aller à", list(pages.keys()))
    page = pages[selection]
    page()

def dashboard_page():
    st.title("Tableau de bord administrateur")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Nombre total d'utilisateurs", len(st.session_state.users))
    
    with col2:
        active_users = len(st.session_state.users[st.session_state.users['last_login'] > pd.Timestamp.now() - pd.Timedelta(days=7)])
        st.metric("Utilisateurs actifs (7 derniers jours)", active_users)
    
    # Graphique des connexions
    st.subheader("Activité des utilisateurs")
    fig = px.scatter(st.session_state.users, x='last_login', y='username', color='is_admin',
                     title="Dernières connexions des utilisateurs",
                     labels={'last_login': 'Dernière connexion', 'username': 'Utilisateur', 'is_admin': 'Administrateur'})
    st.plotly_chart(fig)


def user_management_page():
    st.title("Gestion des utilisateurs")
    

    st.subheader("Liste des utilisateurs")

    conn = sqlite3.connect('users.db')
    users_df = pd.read_sql_query("SELECT * FROM users", conn)
    st.dataframe(users_df)
    
    st.subheader("Générer un lien pour un nouvel utilisateur")
    email = st.text_input("Adresse email")
    #is_admin = st.checkbox("Est administrateur?")
    if st.button("Envoyer le lien de connexion"):
        try:
            send_login_link(email)
            st.success("Un lien de connexion a été envoyé à votre adresse email.")
            st.write("Veuillez vérifier votre boîte de réception et cliquer sur le lien pour vous connecter.")
        except Exception as e:
            st.error(f"Une erreur s'est produite lors de l'envoi de l'email : {str(e)}")
    
    # st.subheader("Supprimer un utilisateur")
    # user_to_delete = st.selectbox("Sélectionnez un utilisateur à supprimer", users_df)
    # if st.button("Supprimer l'utilisateur"):
    #     st.session_state.users = st.session_state.users[st.session_state.users['username'] != user_to_delete]
    #     st.success(f"L'utilisateur {user_to_delete} a été supprimé avec succès.")

def settings_page():
    st.title("Paramètres")
    st.write("Cette page est réservée aux paramètres de l'application.")
    
    st.subheader("Changer le mot de passe administrateur")
    new_password = st.text_input("Nouveau mot de passe", type="password")
    confirm_password = st.text_input("Confirmer le nouveau mot de passe", type="password")
    if st.button("Changer le mot de passe"):
        if new_password == confirm_password:
            admin_index = st.session_state.users.index[st.session_state.users['username'] == 'admin'].tolist()[0]
            st.session_state.users.at[admin_index, 'password'] = hash_password(new_password)
            st.success("Le mot de passe administrateur a été changé avec succès.")
        else:
            st.error("Les mots de passe ne correspondent pas.")

def user_home_page():
    st.title("Accueil utilisateur")
    st.write(f"Bienvenue, {st.session_state.username}!")
    
    st.subheader("Activité récente")
    recent_messages = st.session_state.messages[
        (st.session_state.messages['from'] == st.session_state.username) |
        (st.session_state.messages['to'] == st.session_state.username)
    ].sort_values('timestamp', ascending=False).head(5)
    
    if not recent_messages.empty:
        st.write("Vos messages récents :")
        for _, message in recent_messages.iterrows():
            st.text(f"{message['timestamp']}: De {message['from']} à {message['to']} - {message['message']}")
    else:
        st.write("Vous n'avez pas de messages récents.")

def user_profile_page():
    st.title("Profil utilisateur")
    
    # st.subheader("Informations du profil")
    # profile = st.text_area("Votre profil", user['profile'])
    # if st.button("Mettre à jour le profil"):
    #     user_index = st.session_state.users.index[st.session_state.users['username'] == st.session_state.username].tolist()[0]
    #     st.session_state.users.at[user_index, 'profile'] = profile
    #     st.success("Votre profil a été mis à jour avec succès.")

def user_messages_page():
    st.title("Messages")
    
    st.subheader("Envoyer un message")
    recipient = st.selectbox("Destinataire", st.session_state.users['username'][st.session_state.users['username'] != st.session_state.username])
    message = st.text_area("Message")
    if st.button("Envoyer"):
        new_message = pd.DataFrame({
            'from': [st.session_state.username],
            'to': [recipient],
            'message': [message],
            'timestamp': [pd.Timestamp.now()]
        })
        st.session_state.messages = pd.concat([st.session_state.messages, new_message], ignore_index=True)
        st.success("Message envoyé avec succès.")
    
    st.subheader("Vos messages")
    user_messages = st.session_state.messages[
        (st.session_state.messages['from'] == st.session_state.username) |
        (st.session_state.messages['to'] == st.session_state.username)
    ].sort_values('timestamp', ascending=False)
    
    if not user_messages.empty:
        for _, message in user_messages.iterrows():
            st.text(f"{message['timestamp']}: De {message['from']} à {message['to']} - {message['message']}")
    else:
        st.write("Vous n'avez pas de messages.")


def user_pages():
    st.sidebar.title(f"Bienvenue, {st.session_state.username}")
    
    pages = {
        "Accueil": user_home_page,
        "Profil": user_profile_page,
        "Messages": user_messages_page
    }
    
    selection = st.sidebar.radio("Aller à", list(pages.keys()))
    page = pages[selection]
    page()



if __name__ == "__main__":
    main()