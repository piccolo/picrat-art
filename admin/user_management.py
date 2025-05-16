import streamlit as st
import pandas as pd
import sqlite3
from utils.email_sender import send_login_email

def user_management_page():
    st.title("Gestion des utilisateurs")
    
    st.subheader("Liste des utilisateurs")
    conn = sqlite3.connect('users.db')
    users_df = pd.read_sql_query("SELECT * FROM users", conn)
    st.dataframe(users_df)
    
    st.subheader("Générer un lien pour un nouvel utilisateur")
    email = st.text_input("Adresse email")
    if st.button("Envoyer le lien de connexion"):
        try:
            send_login_email(email)
            st.success("Un lien de connexion a été envoyé à l'adresse email.")
            st.write("L'utilisateur recevra le lien dans sa boîte mail.")
        except Exception as e:
            st.error(f"Erreur: {str(e)}")