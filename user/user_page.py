import streamlit as st

st.header("User Page 1")
st.write(f"You are logged in as {st.session_state.role}.")