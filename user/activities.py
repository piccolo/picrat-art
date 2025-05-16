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
    
    sous_niveau = ""
    if niveau == "Collège":
        sous_niveau = st.selectbox("Classe", ["6e", "5e", "4e", "3e"])
    elif niveau == "Lycée":
        sous_niveau = st.selectbox("Classe", ["Seconde", "Première", "Terminale"])
    elif niveau == "Lycée Pro":
        sous_niveau = st.selectbox("Classe", ["Seconde Bac Pro", "Première Bac Pro", "Terminale Bac Pro", "Seconde CAP", "Terminale CAP"])
    elif niveau == "Post-Bac":
        sous_niveau = st.selectbox("Classe", ["CPGE", "Licence", "Master", "BTS", "Ecole Supérieur"])
    
    frequence = st.selectbox("Fréquence de l'activité", 
                            ["Très souvent (plusieurs fois par semaine)", 
                            "Souvent (Une fois par semaine)", 
                            "Parfois (1 fois par mois)", 
                            "Rarement (quelques fois dans l'année)"])
    st.subheader("Questions PIC-RAT")
    resultat = 0
    interaction = st.radio("Est-ce que la technologie permet aux élèves d'interagir ?",("Oui", "Non"), index=None)
    questionnaire1 = False
    questionnaire2 = False
    
    if interaction == 'Oui':
        resultat  = 1
        questionnaire1 = True
        construction = st.radio("Est-ce que la technologie permet à l'élève de participer à la construction de sa connaissance ?",("Oui", "Non"),index=None)
        if construction == 'Oui':
            resultat = 2
            questionnaire1 = True
    else:
        questionnaire1 = True
        
        
    analogique = st.radio("Est-ce que cette activité peut être réalisée de manière identique en analogique ?",("Oui", "Non"),index=None)
    
    if analogique == 'Non':
        #resultat = resultat + 10
        questionnaire2 = True
        transformation = st.radio("Est-ce que la technologie transforme les tâches d'apprentissage ?",("Oui", "Non"),index=None)
        if transformation == 'Oui':
            resultat = resultat + 10
            questionnaire2 = True
    else:
        questionnaire2 = True
    
    if questionnaire1 & questionnaire2:
        if st.button("Enregistrer l'activité"):
            save_activity(st.session_state.username, name, description, niveau, sous_niveau, frequence, resultat) 
            st.success("Activité enregistrée avec succès!")

    # ...reste du code pour l'ajout d'activité...

def list_activities_page():
    st.title("Mes activités")
    df = get_user_activities()
    if df.empty:
        st.info("Vous n'avez pas encore enregistré d'activités.")
    else:
        st.dataframe(df)