import streamlit as st

st.header("Admin Page")
st.write(f"You are logged in as {st.session_state.role}.")