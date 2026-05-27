import streamlit as st
from components.auth import get_roles


PAGES = [
    {
        "file": "pages/login.py",
        "title": "Đăng nhập",
        "roles": None
    },
    {
        "file": "pages/qr.py",
        "title": "QR",
        "roles": ["admin", "qr"]
    },
    {
        "file": "pages/report_work.py",
        "title": "Báo cáo",
        "roles": ["admin", "manager", "report"]
    },
    {
        "file": "pages/test.py",
        "title": "Test",
        "roles": ["admin"]
    }
]


def create_navigation():
    user_roles = (
        get_roles(st.user["email"])
        if st.user.is_logged_in
        else []
    )

    pages = [
        st.Page(p["file"], title=p["title"])
        for p in PAGES
        if allowed(p["roles"], user_roles)
    ]

    return st.navigation(pages)

def allowed(page_roles, user_roles):
    return (
        page_roles is None and not st.user.is_logged_in
    ) or (
        page_roles and any(r in user_roles for r in page_roles)
    )