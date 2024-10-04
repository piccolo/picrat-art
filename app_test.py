import streamlit as st
import os
import io
import pandas as pd
from hashlib import sha256
import uuid
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import plotly.express as px
import sqlite3
from PIL import Image, ImageDraw

chemin_image = os.path.join("images", "2.png")

def dessiner_disque(image, x, y, rayon, couleur):
    # Créer une nouvelle image avec un canal alpha pour le disque
    disque = Image.new('RGBA', (image.width, image.height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(disque)
    draw.ellipse((x-rayon, y-rayon, x+rayon, y+rayon), fill=couleur)
    
    # Fusionner le disque avec l'image de fond
    return Image.alpha_composite(image.convert('RGBA'), disque)

def creer_image_avec_disques(image_fond, disques):
    # Convertir l'image de fond en mode RGBA si ce n'est pas déjà le cas
    image = image_fond.convert('RGBA')
    for x, y, rayon, couleur in disques:
        image = dessiner_disque(image, x, y, rayon, couleur)
    return image

def picrat_art():
    st.header("Picrat-Art")
    image_fond = Image.open(chemin_image)
    x = 800
    y = 800
    rayon = 100
    couleur = "#3cc62e"
    transparence = 128

    # Convertir la couleur en RGBA avec la transparence
    couleur_rgba = tuple(int(couleur.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (transparence,)
    st.session_state.disques = st.session_state.get('disques', []) + [(x, y, rayon, couleur_rgba)]

    image_resultat = creer_image_avec_disques(image_fond.copy(), st.session_state.get('disques', []))
    # Convertir l'image en bytes pour l'affichage
    buf = io.BytesIO()
    image_resultat.save(buf, format="PNG")
    
    # Afficher l'image résultante
    st.image(buf.getvalue(), caption="Image avec disques", use_column_width=True)


# Configuration pour l'envoi d'emails
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "vincent.roullier@gmail.com"
SMTP_PASSWORD = "hhxg qzst jemv hvxt"

# Initialisation de la base de données
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (email TEXT PRIMARY KEY, link_id TEXT, is_active INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS activities
                 (id INTEGER PRIMARY KEY, email TEXT, niveau TEXT, sous_niveau TEXT, 
                 frequence TEXT, score INTEGER)''')
    conn.commit()
    conn.close()

# Fonction pour ajouter ou mettre à jour un utilisateur
def upsert_user(email, link_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (email, link_id, is_active) VALUES (?, ?, 1)",
              (email, link_id))
    conn.commit()
    conn.close()

# Fonction pour vérifier si un lien est valide
def is_valid_link(link_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT email FROM users WHERE link_id = ? AND is_active = 1", (link_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Fonction pour générer un lien unique
def generate_unique_link():
    return base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8')[:22]

# Fonction pour hacher les mots de passe (pour l'admin)
def hash_password(password):
    return sha256(password.encode()).hexdigest()

# Initialisation des données
@st.cache_resource
def init_data():
    users = pd.DataFrame({
        'username': ['admin', 'user1', 'user2'],
        'password': [hash_password('admin123'), '', ''],
        'is_admin': [True, False, False],
        'unique_link': ['', generate_unique_link(), generate_unique_link()],
        'last_login': [pd.Timestamp.now(), pd.Timestamp.now() - pd.Timedelta(days=2), pd.Timestamp.now() - pd.Timedelta(days=5)]
    })
    return users, {}

def send_login_link(email):
    unique_id = str(uuid.uuid4())
    #login_link = f"http://localhost:8501/?id={unique_id}"
    login_link = f"http://picrat-art.streamlit.app/?id={unique_id}"
    
    upsert_user(email, unique_id)

    message = MIMEMultipart()
    message["From"] = SMTP_USERNAME
    message["To"] = email
    message["Subject"] = "Votre lien de connexion"
    body = f"Voici votre lien de connexion unique : {login_link}"
    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(message)

# Fonction d'authentification
def authenticate(username, password):
    user = st.session_state.users[st.session_state.users['username'] == username]
    if not user.empty and user.iloc[0]['is_admin']:
        if user.iloc[0]['password'] == hash_password(password):
            return True
    return False

# Page principale
def main():
    init_db()
    st.title("Application avec authentification par lien unique")
    
    if 'users' not in st.session_state or 'active_links' not in st.session_state:
        st.session_state.users, st.session_state.active_links = init_data()
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Vérification du lien unique dans l'URL
    #params = st.query_params()
    unique_id = st.query_params.get("id")
    if unique_id:
        email = is_valid_link(unique_id)
        if email:
            st.success(f"Connecté en tant que {email}")
            st.session_state.logged_in = True
            st.session_state.is_admin = False
            st.session_state.username = email
            st.query_params.update()
    if not st.session_state.logged_in:
        username = st.text_input("Nom d'utilisateur (admin)")
        password = st.text_input("Mot de passe", type="password")
        if st.button("Se connecter"):
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.session_state.username = username
                st.query_params.update()    
                st.rerun()
            else:
                st.error("Authentification échouée")
    else:
        if st.sidebar.button("Se déconnecter"):
            st.session_state.logged_in = False
            st.query_params.update()    
            st.rerun()
        
        if st.session_state.is_admin:
            admin_pages()
        else:
            user_pages()

def admin_pages():
    st.sidebar.title(f"Bienvenue, {st.session_state.username}")
    
    pages = {
        "Tableau de bord": dashboard_page,
        "Gestion des utilisateurs": user_management_page,
        "Activités": admin_list_activity_page,
        "Picrat_art": picrat_art,
        "Paramètres": settings_page

    }
    
    selection = st.sidebar.radio("Aller à", list(pages.keys()))
    page = pages[selection]
    page()

def dashboard_page():
    st.title("Tableau de bord administrateur")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Nombre total d'utilisateurs", len(st.session_state.users))
    
    with col2:
        active_users = len(st.session_state.users[st.session_state.users['last_login'] > pd.Timestamp.now() - pd.Timedelta(days=7)])
        st.metric("Utilisateurs actifs (7 derniers jours)", active_users)
    
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
            send_login_link(email)
            st.success("Un lien de connexion a été envoyé à votre adresse email.")
            st.write("Veuillez vérifier votre boîte de réception et cliquer sur le lien pour vous connecter.")
        except Exception as e:
            st.error(f"Une erreur s'est produite lors de l'envoi de l'email : {str(e)}")
def admin_list_activity_page():
    st.title("Listes des activités enregistrées")
    df = get_all_activity()
    st.write(df)

def settings_page():
    st.title("Paramètres")
    st.write("Cette page est réservée aux paramètres de l'application.")
    
    st.subheader("Changer le mot de passe administrateur")
    new_password = st.text_input("Nouveau mot de passe", type="password")
    confirm_password = st.text_input("Confirmer le nouveau mot de passe", type="password")
    if st.button("Changer le mot de passe"):
        if new_password == confirm_password:
            admin_index = st.session_state.users.index[st.session_state.users['username'] == 'admin'].tolist()[0]
            st.session_state.users.at[admin_index, 'password'] = hash_password(new_password)
            st.success("Le mot de passe administrateur a été changé avec succès.")
        else:
            st.error("Les mots de passe ne correspondent pas.")

def user_home_page():
    st.title("Accueil utilisateur")
    st.write(f"Bienvenue, {st.session_state.username}!")

def save_activity(email, niveau, sous_niveau, frequence, score):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''INSERT INTO activities 
                 (email, niveau, sous_niveau, frequence, score) 
                 VALUES (?, ?, ?, ?, ?)''', 
              (email, niveau, sous_niveau, frequence, score))
    conn.commit()
    conn.close()

def user_add_activity_page():
    st.title("Enregistrer une activité")

    niveau = st.selectbox("Niveau", ["Collège", "Lycée", "Post-Bac"])
        
    sous_niveau = ""
    if niveau == "Collège":
        sous_niveau = st.selectbox("Classe", ["6e", "5e", "4e", "3e"])
    elif niveau == "Lycée":
        sous_niveau = st.selectbox("Classe", ["Seconde", "Première", "Terminale"])
    
    frequence = st.selectbox("Fréquence de l'activité", 
                            ["Très souvent (plusieurs fois par semaine)", 
                            "Souvent (Une fois par semaine)", 
                            "Parfois (1 fois par mois)", 
                            "Rarement (quelques fois dans l'année)"])
    
    st.subheader("Questions PIC-RAT")

    resultat = 0
    interaction = st.radio("Est-ce que la technologie permet aux élèves d'interagir ?",("Oui", "Non"), index=None)
    if interaction == 'Oui':
        resultat  = 1
        construction = st.radio("Est-ce que la technologie permet à l'élève de participer à la construction de sa connaissance ?",("Oui", "Non"),index=None)
        if construction == 'Oui':
            resultat = 2
        
    analogique = st.radio("Est-ce que cette activité peut être réalisée de manière identique en analogique ?",("Oui", "Non"),index=None)
    if analogique == 'Oui':
        resultat = resultat + 10
        transformation = st.radio("Est-ce que la technologie transforme les tâches d'apprentissage ?",("Oui", "Non"),index=None)
        if transformation == 'Oui':
            resultat = resultat + 10
        
    if st.button("Enregistrer l'activité"):
        save_activity(st.session_state.username, niveau, sous_niveau, frequence, resultat) 
        st.success("Activité enregistrée avec succès!")

def get_all_activity():
    conn = sqlite3.connect('users.db')
    query = "SELECT email, niveau, sous_niveau, frequence, score FROM activities"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_user_activity():
    conn = sqlite3.connect('users.db')
    query = "SELECT email, niveau, sous_niveau, frequence, score FROM activities WHERE email = ?"
    df = pd.read_sql_query(query, conn, params=(st.session_state.username,))
    conn.close()
    return df

def user_activity_list_page():
    st.title("Liste des activités")
    df = get_user_activity()
    st.write(df)

def user_pages():
    st.sidebar.title(f"Bienvenue, {st.session_state.username}")
    
    pages = {
        "Accueil": user_home_page,
        "Listes de activites" : user_activity_list_page,
        "Ajouter une activite": user_add_activity_page,
    }
    
    selection = st.sidebar.radio("Aller à", list(pages.keys()))
    page = pages[selection]
    page()



if __name__ == "__main__":
    main()