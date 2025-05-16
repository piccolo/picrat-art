import streamlit as st
import sqlite3
import pandas as pd

def save_activity(email, name, description, niveau, sous_niveau, frequence, score):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''INSERT INTO activities 
                 (email, name, description, niveau, sous_niveau, frequence, score) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', 
              (email, name, description, niveau, sous_niveau, frequence, score))
    conn.commit()
    conn.close()

def get_user_activities():
    conn = sqlite3.connect('users.db')
    query = "SELECT name, description, niveau, sous_niveau, frequence, score FROM activities WHERE email = ?"
    df = pd.read_sql_query(query, conn, params=(st.session_state.username,))
    conn.close()
    return df

def add_activity_page():
    st.title("Enregistrer une activité")
    
    name = st.text_input("Nom de l'activité")
    description = st.text_area("Description de l'activité")
    niveau = st.selectbox("Niveau", ["Collège", "Lycée", "Lycée Pro", "Post-Bac"])
    
    # ...reste du code pour l'ajout d'activité...

def list_activities_page():
    st.title("Mes activités")
    df = get_user_activities()
    if df.empty:
        st.info("Vous n'avez pas encore enregistré d'activités.")
    else:
        st.dataframe(df)