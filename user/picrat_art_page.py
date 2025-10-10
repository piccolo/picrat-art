import streamlit as st
from PIL import Image, ImageDraw
from user.activities import get_user_activities
import os
import io

chemin_image = os.path.join("images", "2.png")

CODE_COORDONNEES= {
    0 : (630, 1140),
    1 : (1010, 1140),
    2 : (1390, 1140),
    10 : (630, 760),
    11 : (1010, 760),
    12 : (1390, 760),
    20 : (630, 380),
    21 : (1010, 380),
    22 : (1390, 380),
}

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


def display():
    st.title("Picrat-Art")
    st.write("Bienvenue sur la page Picrat-Art!")
    ids = st.session_state.get('filtered_ids', [])
    st.write(f"IDs reçus : {ids}")

    image_fond = Image.open(chemin_image)
    x = 800
    y = 800
    rayon = 100
    couleur = "#3cc62e"
    transparence = 64

    df = get_user_activities()


    df_selectionne = df[df[df.columns[0]].isin(ids)]
    st.session_state.disques = []

    # Convertir la couleur en RGBA avec la transparence
    couleur_rgba = tuple(int(couleur.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (transparence,)
    
    for i, element in enumerate(ids):
        # Pour chaque élément, dessiner un disque avec des paramètres variables
        score = df_selectionne.iloc[i].get('score', 0)  # Remplacez 'score' par le nom de la colonne appropriée
        frequence = df_selectionne.iloc[i].get('frequence', 'Rarement (quelques fois dans l\'année)')
        print(frequence)

        if frequence == "Très souvent (plusieurs fois par semaine)":
            rayon = 150
        elif frequence == "Souvent (Une fois par semaine)":
            rayon = 120
        elif frequence == "Parfois (1 fois par mois)":
            rayon = 90
        else:
            rayon = 60

        # Ajouter le disque à la liste dans le session state
        st.session_state.disques = st.session_state.get('disques', []) + [(CODE_COORDONNEES[score][0],CODE_COORDONNEES[score][1], rayon, couleur_rgba)]

    #st.session_state.disques = st.session_state.get('disques', []) + [(x, y, rayon, couleur_rgba)]

    image_resultat = creer_image_avec_disques(image_fond.copy(), st.session_state.get('disques', []))
    # Convertir l'image en bytes pour l'affichage
    buf = io.BytesIO()
    image_resultat.save(buf, format="PNG")
    
    # Afficher l'image résultante
    st.image(buf.getvalue(), caption="Image avec disques", use_container_width=True)


# Ici tu continues la logique temporaire