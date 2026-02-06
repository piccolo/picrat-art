import streamlit as st
from auth.auth import login_page, verify_auth
from admin.dashboard import dashboard_page
from admin.user_management import user_management_page
from admin.activities import admin_list_activity_page
from user.home import user_home_page
from user.activities import add_activity_page, list_activities_page
from user.picrat_art_page import display
from admin.picrat_art_page import admin_display
from database.models import init_db
from auth.auth import check_valid_link

def admin_interface():
    st.sidebar.title(f"Bienvenue, {st.session_state.username}")
    
    pages = {
        "Tableau de bord": dashboard_page,
        "Gestion des utilisateurs": user_management_page,
        "Activités": admin_list_activity_page,
        "Picrat-Art": admin_display,
    }
    
    selection = st.sidebar.radio("Navigation", list(pages.keys()))
    pages[selection]()

def user_interface():
    st.sidebar.title(f"Bienvenue, {st.session_state.username}")
    
    pages = {
        "Accueil": user_home_page,
        "Mes activités": list_activities_page,
        "Nouvelle activité": add_activity_page,
        "Picrat-Art": display,
    }
    
    selection = st.sidebar.radio("Navigation", list(pages.keys()))
    pages[selection]()

def main():
    init_db()
    st.title("PicRat-Art")
    
    check_valid_link()

    if not verify_auth():
        login_page()
    else:
        if st.session_state.is_admin:
            admin_interface()
        else:
            user_interface()

if __name__ == "__main__":
    main()
