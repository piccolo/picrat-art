import streamlit as st
from PIL import Image, ImageDraw
import io
import os

def dessiner_disque(image, x, y, rayon, couleur):
    # Créer une nouvelle image avec un canal alpha pour le disque
    st.write(couleur)
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

# Configuration de la page Streamlit
st.set_page_config(page_title="Dessin de disques transparents sur image")
st.title("Dessin de disques transparents sur une image de fond")

# Chemin vers le dossier contenant les images
dossier_images = "images"

# Liste des fichiers d'images dans le dossier
fichiers_images = [f for f in os.listdir(dossier_images) if f.endswith(('.png', '.jpg', '.jpeg'))]

# Sélection de l'image de fond
nom_fichier = st.selectbox("Choisissez une image de fond", fichiers_images)

if nom_fichier:
    chemin_image = os.path.join(dossier_images, nom_fichier)
    image_fond = Image.open(chemin_image)

    # Interface pour ajouter des disques
    st.sidebar.header("Ajouter un disque")
    x = st.sidebar.number_input("Coordonnée X", value=100, min_value=0)
    y = st.sidebar.number_input("Coordonnée Y", value=100, min_value=0)
    rayon = st.sidebar.number_input("Rayon", value=50, min_value=1)
    couleur = st.sidebar.color_picker("Couleur", "#FF0000")
    transparence = st.sidebar.slider("Transparence", 0, 255, 128)
    
    # Convertir la couleur en RGBA avec la transparence
    couleur_rgba = tuple(int(couleur.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (transparence,)
    st.write(couleur_rgba)

    # Bouton pour ajouter un disque
    if st.sidebar.button("Ajouter un disque"):
        st.session_state.disques = st.session_state.get('disques', []) + [(x, y, rayon, couleur_rgba)]

    # Afficher et permettre la modification des disques existants
    st.sidebar.header("Disques existants")
    for i, (x, y, r, c) in enumerate(st.session_state.get('disques', [])):
        st.sidebar.text(f"Disque {i+1}: ({x}, {y}), rayon={r}, couleur={c}")

    # Bouton pour effacer tous les disques
    if st.sidebar.button("Effacer tous les disques"):
        st.session_state.disques = []

    # Créer et afficher l'image avec les disques
    image_resultat = creer_image_avec_disques(image_fond.copy(), st.session_state.get('disques', []))
    
    # Convertir l'image en bytes pour l'affichage
    buf = io.BytesIO()
    image_resultat.save(buf, format="PNG")
    
    # Afficher l'image résultante
    st.image(buf.getvalue(), caption=f"Image avec disques transparents: {nom_fichier}", use_column_width=True)

else:
    st.write("Aucune image trouvée dans le dossier spécifié.")