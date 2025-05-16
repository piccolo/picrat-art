import streamlit as st
import pandas as pd

def dashboard_page():
    st.title("Tableau de bord administrateur")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Nombre total d'utilisateurs", len(st.session_state.users))
    
    with col2:
        active_users = len(st.session_state.users[st.session_state.users['last_login'] > pd.Timestamp.now() - pd.Timedelta(days=7)])
        st.metric("Utilisateurs actifs (7 derniers jours)", active_users)