import streamlit as st
import sqlite3
import datetime
import pandas as pd

def save_activity(email, name, description, niveau, sous_niveau, frequence, score,date_creation):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    date_creation = datetime.datetime.now().isoformat()
    c.execute('''INSERT INTO activities 
                 (email, name, description, niveau, sous_niveau, frequence, score, date_creation) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
              (email, name, description, niveau, sous_niveau, frequence, score, date_creation))
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
        resultat  = 10
        questionnaire1 = True
        construction = st.radio("Est-ce que la technologie permet à l'élève de participer à la construction de sa connaissance ?",("Oui", "Non"),index=None)
        if construction == 'Oui':
            resultat = 20
            questionnaire1 = True
    else:
        questionnaire1 = True
        
        
    analogique = st.radio("Est-ce que cette activité peut être réalisée de manière identique en analogique ?",("Oui", "Non"),index=None)
    
    if analogique == 'Non':
        #resultat = resultat + 10
        questionnaire2 = True
        transformation = st.radio("Est-ce que la technologie transforme les tâches d'apprentissage ?",("Oui", "Non"),index=None)
        if transformation == 'Oui':
            resultat = resultat + 2
            questionnaire2 = True
        else:
            resultat = resultat + 1
#            questionnaire2 = False
    else:
        questionnaire2 = True
    
    if questionnaire1 & questionnaire2:
        if st.button("Enregistrer l'activité"):
            save_activity(st.session_state.username, name, description, niveau, sous_niveau, frequence, resultat,datetime.datetime.now().isoformat()) 
            st.success("Activité enregistrée avec succès!")

    # ...reste du code pour l'ajout d'activité...

def list_activities_page():
    st.title("Mes activités")
    df = get_user_activities()
    
    # Conversion explicite en type object (texte)
    df['score'] = df['score'].astype(object)
    df.loc[df['score'] == 0, 'score'] = "PR"
    df.loc[df['score'] == 1, 'score'] = "PA"
    df.loc[df['score'] == 2, 'score'] = "PT"
    
    df.loc[df['score'] == 10, 'score'] = "IR"
    df.loc[df['score'] == 11, 'score'] = "IA"
    df.loc[df['score'] == 12, 'score'] = "IT"
    
    df.loc[df['score'] == 20, 'score'] = "CR"
    df.loc[df['score'] == 21, 'score'] = "CA"
    df.loc[df['score'] == 22, 'score'] = "CT"
    
    if df.empty:
        st.info("Vous n'avez pas encore enregistré d'activités.")
    else:
        selection = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row"  # ou "single-row" pour une seule sélection
        )
        
    st.session_state['filtered_ids'] = []  # Réinitialiser les IDs filtrés à chaque affichage de la page
    # Récupérer les indices des lignes sélectionnées
    if selection.selection.rows:
        selected_indices = selection.selection.rows
        selected_rows = df.iloc[selected_indices]
        
        st.success(f"✅ {len(selected_rows)} activité(s) sélectionnée(s)")
        
        with st.expander("Voir les activités sélectionnées"):
            st.dataframe(selected_rows)

    #     col1, col2 = st.columns(2)
    #     with col1:
    #         if not df.empty and 'niveau' in df.columns:
    #             niveau_filter = st.multiselect(
    #                 "Filtrer par niveau",
    #                 options=df['niveau'].dropna().unique()
    #             )
    #         else:
    #             niveau_filter = []
    #     with col2:
    #         if not df.empty and 'sous_niveau' in df.columns:
    #             sous_niveau_filter = st.multiselect(
    #                 "Filtrer par sous-niveau",
    #                 options=df['sous_niveau'].dropna().unique()
    #             )
    #         else:
    #             sous_niveau_filter = []
        
    #     # Application des filtres
    #     if niveau_filter:
    #         df = df[df['niveau'].isin(niveau_filter)]
    #     if sous_niveau_filter:
    #         df = df[df['sous_niveau'].isin(sous_niveau_filter)]
        
    #     # Affichage des statistiques
    #     st.subheader("Statistiques")
    #     #col1 = st.columns(1)
    #    # with col1:
    #     st.metric("Nombre total d'activités", len(df))
    #     #with col3:
    #     #    if 'score' in df.columns:
    #     #        st.metric("Score moyen", round(df['score'].mean(), 2))
        
    #     # Affichage du tableau des activités
    #     st.subheader("Détail des activités")
    #    if not df.empty:
    #        st.dataframe(df)
       
    else:
        st.info("Aucune activité enregistrée pour le moment.")

    if st.button("Générer Picrat-Art", type="primary"):
        st.session_state['filtered_ids'] = list(selected_rows[selected_rows.columns[0]])  # ou n’importe quelle info utile
