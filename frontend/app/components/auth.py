import streamlit as st


USERS = {
    "trinhthanh2002e@gmail.com": [
        "admin",
        "manager",
        "report",
        "qr"
    ],

    "staff@gmail.com": [
        "report"
    ],

    "leader@gmail.com": [
        "manager",
        "report"
    ]
}


def login_ui():
    if not st.user.is_logged_in:
        if st.button("Đăng nhập Google"):
            st.login()
        st.stop()


def get_user():
    return {
        "email": st.user["email"],
        "name": st.user["name"],
        "picture": st.user["picture"]
    }


def get_roles(email):
    return USERS.get(email, [])


def require_role(*allowed_roles):
    login_ui()

    user = get_user()
    roles = get_roles(user["email"])

    if not any(role in roles for role in allowed_roles):
        st.error("Không có quyền truy cập")
        st.stop()

    return user, roles


def redirect():
    login_ui()

    user = get_user()
    roles = get_roles(user["email"])

    if "admin" in roles or "qr" in roles:
        st.switch_page("pages/qr.py")

    elif "report" in roles:
        st.switch_page("pages/report_work.py")

    else:
        st.switch_page("main.py")