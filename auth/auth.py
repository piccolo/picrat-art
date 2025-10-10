import streamlit as st
import uuid
from database.models import upsert_user
from utils.email_sender import send_login_email
import sqlite3

# Fonction pour vérifier si un lien est valide
def is_valid_link(link_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT email FROM users WHERE link_id = ? AND is_active = 1", (link_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def check_valid_link():
    unique_id = st.query_params.get("id")
    print(unique_id)
    if unique_id:
        email = is_valid_link(unique_id)
        st.session_state.logged_in = True
        st.session_state.is_admin = False
        st.session_state.username = email
    else:
        print("not valid link")

def verify_auth():
    """Vérifie si l'utilisateur est authentifié"""

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    return st.session_state.logged_in

def login_page():
    st.title("Bienvenue sur PicRat-Art")
    
    tab1, tab2 = st.tabs(["Créer un compte", "Connexion"])
        
    
    with tab1:
        # Création de compte
        st.subheader("Créer un compte")
        st.write("Entrez votre email pour recevoir un lien de connexion unique")
        email = st.text_input("Adresse email")
        email = email.lower()
        if st.button("Créer un compte"):
            try:
                unique_id = str(uuid.uuid4())
                upsert_user(email, unique_id)
                send_login_email(email,unique_id)
                st.success("Un lien de connexion a été envoyé à votre adresse email.")
                st.write("Veuillez vérifier votre boîte de réception et cliquer sur le lien pour vous connecter.")
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de l'envoi de l'email : {str(e)}")
    with tab2:
        # Connexion admin
        st.subheader("Connexion administrateur")
        username = st.text_input("Nom d'utilisateur (admin)")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if (username, password):
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.session_state.username = username
                st.query_params.update()    
                st.rerun()
            else:
                st.error("Authentification échouée")

    """ if not st.session_state.get("logged_in", False):
        email = st.text_input("Adresse email")
        if st.button("Créer un compte / Se connecter"):
            try:
                unique_id = str(uuid.uuid4())
                upsert_user(email, unique_id)
                send_login_email(email, unique_id)
                st.success("Un lien de connexion a été envoyé à votre adresse email.")
            except Exception as e:
                st.error(f"Erreur: {str(e)}") """