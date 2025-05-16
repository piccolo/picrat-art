import streamlit as st

def user_home_page():
    st.title("Accueil utilisateur")
    st.write(f"Bienvenue, {st.session_state.username}!")
    
    st.markdown("""
    ### Que souhaitez-vous faire ?
    - Consultez vos activités enregistrées
    - Ajoutez une nouvelle activité
    - Utilisez PicRat-Art
    """)