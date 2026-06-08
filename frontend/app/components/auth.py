import streamlit as st


SUPER_ADMIN_ROLE = "super_admin"


USERS = {
    "guest@gmail.com": [
        "admin",
        "manager",
        "report",
        "qr",
        "mes",
        "bravo",
    ],

    "trinhthanh2002e@gmail.com": [
        "admin",
        "manager",
        "report",
    ],
}


# =========================
# MODULE PERMISSIONS
# =========================

MODULE_PERMISSIONS = {
    "qr": ["qr", "manager"],
    "report": ["admin", "manager", "report"],
    "mes": ["mes",
        "manager"],
    "bravo": ["bravo"],
    "other": None,
}


# =========================
# TAB PERMISSIONS
# =========================

TAB_PERMISSIONS = {
    "pages/qr.py": ["admin", "qr", "manager"],

    "pages/report_work.py": [
        "manager",
        "report",
    ],

    "pages/MES/get_station.py": ["mes","manager"],
    "pages/MES/qr_mes.py": ["mes"],

    "pages/bravo/check.py": ["bravo"],

    "pages/login.py": None,
    "pages/test.py": None,
    "pages/test_2.py": None,
    "pages/wifi_qr.py": None,
}


# =========================
# USER
# =========================

def get_user():

    if not hasattr(st, "user"):
        return None

    if not hasattr(st.user, "is_logged_in"):
        return None

    if not st.user.is_logged_in:
        return None

    return {
        "email": st.user.get("email"),
        "name": st.user.get("name"),
        "picture": st.user.get("picture"),
    }


# =========================
# LOGIN UI
# =========================

def login_ui():

    if not st.user.get("is_logged_in", False):

        st.info("Chưa đăng nhập")

        if st.button("Đăng nhập Google"):
            st.login()

        st.stop()


# =========================
# ROLE
# =========================

def get_roles(email):
    return USERS.get(email, [])


# =========================
# PERMISSION CORE
# =========================

def can_access(allowed_roles, user_roles):

    # None = public
    if allowed_roles is None:
        return True

    # super admin
    if SUPER_ADMIN_ROLE in user_roles:
        return True

    return any(role in user_roles for role in allowed_roles)


def can_access_module(module_key, user_roles):

    allowed_roles = MODULE_PERMISSIONS.get(
        module_key,
        [SUPER_ADMIN_ROLE],
    )

    return can_access(
        allowed_roles,
        user_roles,
    )


def can_access_tab(page_file, user_roles):

    allowed_roles = TAB_PERMISSIONS.get(
        page_file,
        [SUPER_ADMIN_ROLE],
    )

    return can_access(
        allowed_roles,
        user_roles,
    )


# =========================
# REQUIRE
# =========================

def require_role(*allowed_roles):

    user = get_user()

    if user is None:
        st.error("Chưa đăng nhập")
        st.stop()

    roles = get_roles(user["email"])

    if not can_access(list(allowed_roles), roles):
        st.error("Không có quyền truy cập")
        st.stop()

    return user, roles


def require_module(module_key):

    user = get_user()

    if user is None:
        st.error("Chưa đăng nhập")
        st.stop()

    roles = get_roles(user["email"])

    if not can_access_module(module_key, roles):
        st.error("Không có quyền truy cập module này")
        st.stop()

    return user, roles


def require_tab(page_file):

    # support dict page
    if isinstance(page_file, dict):
        page_file = page_file.get("file")

    user = get_user()

    if user is None:
        st.error("Chưa đăng nhập")
        st.stop()

    roles = get_roles(user["email"])

    if not can_access_tab(page_file, roles):
        st.error("Không có quyền truy cập chức năng này")
        st.stop()

    return user, roles


# =========================
# REDIRECT
# =========================

def redirect():

    # tránh rerun loop
    if st.session_state.get("redirected"):
        return

    user = get_user()

    if user is None:
        return

    roles = get_roles(user["email"])

    # QR
    if (
        can_access_module("qr", roles)
        and
        can_access_tab("pages/qr.py", roles)
    ):

        st.session_state["active_module_key"] = "qr"

        st.session_state["active_page_file"] = "pages/qr.py"

    # REPORT
    elif (
        can_access_module("report", roles)
        and
        can_access_tab("pages/report_work.py", roles)
    ):

        st.session_state["active_module_key"] = "report"

        st.session_state["active_page_file"] = "pages/report_work.py"

    else:

        st.session_state.pop("active_module_key", None)
        st.session_state.pop("active_page_file", None)

    st.session_state["redirected"] = True

    st.rerun()


# =========================
# LOGOUT
# =========================

def logout():

    st.session_state.pop("redirected", None)
    st.session_state.pop("active_module_key", None)
    st.session_state.pop("active_page_file", None)

    st.logout()

