import streamlit as st
import pandas as pd
import sqlite3

def get_activities():
    conn = sqlite3.connect('users.db')
    query = "SELECT id, email, name, description, niveau, sous_niveau, frequence, score FROM activities"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def admin_list_activity_page():
    st.title("Liste des activités")
    
    # Connexion à la base de données
    conn = sqlite3.connect('users.db')
    
    # Récupération de toutes les activités avec le mail de l'utilisateur
    # query = """
    # SELECT activities.*, users.email 
    # FROM activities 
    # JOIN users ON activities.email = users.email
    # ORDER BY activities.date_creation DESC
    # """
    query = """
    SELECT activities.id,
       activities.email,
       activities.name,
       activities.description,
       activities.niveau,
       activities.sous_niveau,
       activities.frequence,
       activities.score,
       activities.date_creation,
       users.email AS user_email
    FROM activities
    JOIN users ON activities.email = users.email
    ORDER BY activities.date_creation DESC
    """
    try:
        df = pd.read_sql_query(query, conn)
        # Ajout de filtres

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
        selected_rows = pd.DataFrame()
        # Récupérer les indices des lignes sélectionnées
        if selection.selection.rows:
            selected_indices = selection.selection.rows
            selected_rows = df.iloc[selected_indices]
            
            st.success(f"✅ {len(selected_rows)} activité(s) sélectionnée(s)")
            
            with st.expander("Voir les activités sélectionnées"):
                st.dataframe(selected_rows)

        # col1, col2 = st.columns(2)
        # with col1:
        #     if not df.empty and 'niveau' in df.columns:
        #         niveau_filter = st.multiselect(
        #             "Filtrer par niveau",
        #             options=df['niveau'].dropna().unique()
        #         )
        #     else:
        #         niveau_filter = []
        # with col2:
        #     if not df.empty and 'email' in df.columns:
        #         user_filter = st.multiselect(
        #             "Filtrer par utilisateur",
        #             options=df['email'].dropna().unique()
        #         )
        #     else:
        #         user_filter = []
        
        # # Application des filtres
        # if niveau_filter:
        #     df = df[df['niveau'].isin(niveau_filter)]
        # if user_filter:
        #     df = df[df['email'].isin(user_filter)]
        
        # # Affichage des statistiques
        # st.subheader("Statistiques")
        # col1, col2, col3 = st.columns(3)
        # with col1:
        #     st.metric("Nombre total d'activités", len(df))
        # with col2:
        #     st.metric("Nombre d'utilisateurs actifs", df['email'].nunique())
        # with col3:
        #     if 'score' in df.columns:
        #         st.metric("Score moyen", round(df['score'].mean(), 2))
        
        # Affichage du tableau des activités
        else:
           st.info("Aucune activité enregistrée pour le moment.")

        if st.button("Générer Picrat-Art", type="primary"):
            if (len(selected_rows) > 0):
                st.session_state['filtered_ids'] = list(selected_rows[selected_rows.columns[0]])  # ou n’importe quelle info utile
                st.success("✅ Activités sélectionnées pour Picrat-Art")
            else:
                st.session_state['filtered_ids'] = list(df[df.columns[0]])  # ou n’importe quelle info utile
                
    except Exception as e:
        st.error(f"Erreur lors de la récupération des activités : {str(e)}")
    finally:
        conn.close()

def get_activity_stats():
    """Fonction utilitaire pour obtenir les statistiques des activités"""
    conn = sqlite3.connect('users.db')
    stats = {}
    try:
        cursor = conn.cursor()
        
        # Nombre total d'activités
        cursor.execute("SELECT COUNT(*) FROM activities")
        stats['total_activities'] = cursor.fetchone()[0]
        
        # Nombre d'utilisateurs uniques
        cursor.execute("SELECT COUNT(DISTINCT email) FROM activities")
        stats['unique_users'] = cursor.fetchone()[0]
        
        # Score moyen
        cursor.execute("SELECT AVG(score) FROM activities")
        stats['average_score'] = round(cursor.fetchone()[0] or 0, 2)
        
    except Exception as e:
        print(f"Erreur lors de la récupération des statistiques : {e}")
        stats = {'total_activities': 0, 'unique_users': 0, 'average_score': 0}
    finally:
        conn.close()
    
    return stats