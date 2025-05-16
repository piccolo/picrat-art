import streamlit as st
import uuid
from database.models import upsert_user
from utils.email_sender import send_login_email

def verify_auth():
    """Vérifie si l'utilisateur est authentifié"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    return st.session_state.logged_in

def login_page():
    st.title("Bienvenue sur PicRat-Art")
    
    tab1, tab2 = st.tabs(["Connexion", "Créer un compte"])
        
    with tab1:
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

    with tab2:
        # Création de compte
        st.subheader("Créer un compte")
        st.write("Entrez votre email pour recevoir un lien de connexion unique")
        email = st.text_input("Adresse email")
        if st.button("Créer un compte"):
            try:
                send_login_link(email)
                st.success("Un lien de connexion a été envoyé à votre adresse email.")
                st.write("Veuillez vérifier votre boîte de réception et cliquer sur le lien pour vous connecter.")
            except Exception as e:
                st.error(f"Une erreur s'est produite lors de l'envoi de l'email : {str(e)}")

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