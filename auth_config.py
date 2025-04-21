import streamlit as st
import streamlit_authenticator as stauth

names = ['Athlete Name']
usernames = ['athlete']
passwords = ['password']
hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(
    names, usernames, hashed_passwords, 'triathlete_dashboard', 'abc_key'
)

name, auth_status = authenticator.login('Login', 'main')

if auth_status:
    st.success(f"Welcome {name}")
elif auth_status is False:
    st.error("Login failed")
elif auth_status is None:
    st.warning("Enter credentials")
