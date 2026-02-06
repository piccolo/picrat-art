import streamlit as st
import pandas as pd
import sqlite3
import uuid
from database.models import upsert_user
from utils.email_sender import send_login_email

def user_management_page():
    st.title("Gestion des utilisateurs")
    
    st.subheader("Liste des utilisateurs")
    conn = sqlite3.connect('users.db')
    users_df = pd.read_sql_query("SELECT * FROM users", conn)

    # Affiche dataframe après modification
    st.dataframe(users_df)

    #st.data_editor(users_df, num_rows="dynamic")

    
    # Ajouter une colonne de cases à cocher
    users_df['supprimer'] = False
    # Afficher le DataFrame avec des cases à cocher
    edited_df = st.data_editor(
        users_df,
        column_config={
            "supprimer": st.column_config.CheckboxColumn("Supprimer")
        },
        hide_index=True
    )

    # Récupérer les lignes sélectionnées
    selected_rows = edited_df[edited_df['supprimer']]  
    # Bouton pour supprimer les lignes sélectionnées
    if st.button('Supprimer les lignes sélectionnées'):
        if not selected_rows.empty:
            delete_selected_rows(selected_rows['email'].tolist())
            st.success(f"{len(selected_rows )} ligne(s) supprimée(s) avec succès!")
            st.rerun()  # Recharger l'application pour afficher les données mises à jour
        else:
            st.warning("Aucune ligne sélectionnée.")

    st.subheader("Générer un lien pour un nouvel utilisateur")
    
    email = st.text_input("Adresse email")
    if st.button("Envoyer le lien de connexion"):
        try:
            unique_id = str(uuid.uuid4())
            upsert_user(email, unique_id)
            send_login_email(email,unique_id)
            st.success("Un lien de connexion a été envoyé à l'adresse email.")
            st.write("L'utilisateur recevra le lien dans sa boîte mail.")
        except Exception as e:
            st.error(f"Erreur: {str(e)}")
    
# Fonction pour supprimer les lignes sélectionnées de la base de données
def delete_selected_rows(ids):
    conn = sqlite3.connect('users.db')
    try:
        # D'abord, supprimer les lignes liées dans table_liee
        for id in ids:
            conn.execute('DELETE FROM activites WHERE email = ?', (id,))
        # Ensuite, supprimer les lignes dans table_principal
        for id in ids:
            conn.execute('DELETE FROM users WHERE email = ?', (id,))
        conn.commit()
        st.success(f"{len(ids)} ligne(s) supprimée(s) avec succès, y compris leurs dépendances !")
    except Exception as e:
        conn.rollback()
        st.error(f"Erreur lors de la suppression : {e}")
    finally:
        conn.close()

    # for id in ids:
    #     conn.execute('DELETE FROM users WHERE email = ?', (id,))
    # conn.commit()
    # conn.close()
