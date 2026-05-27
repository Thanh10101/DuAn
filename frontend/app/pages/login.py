import streamlit as st
from components.auth import redirect

st.title("Google Login Test")

st.write(st.user)

if not st.user["is_logged_in"]:
    if st.button("Đăng nhập Google"):
        st.login()

else:
    st.success("Đăng nhập thành công")

    st.write("Name:", st.user.get("name"))
    st.write("Email:", st.user.get("email"))
    redirect()

    if st.user.get("picture"):
        st.image(st.user["picture"], width=120)

    if st.button("Logout"):
        st.logout()

    st.json(dict(st.user))