import sys
from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parent

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


from components.auth import (
    get_roles,
    get_user,
    redirect,
    require_tab,
    logout,
)

from module import (
    get_module_by_key,
    get_visible_modules,
)

from module_home import render_module_home

from navigations import (
    register_navigation_shell,
    run_page,
)

from sidebar import (
    ACTIVE_MODULE_KEY,
    clear_active_module,
    render_function_sidebar,
)


# =========================
# LOGIN WIDGET
# =========================

def widget_login():

    st.title("Google Login Test")

    if not st.user.get("is_logged_in", False):

        if st.button("Đăng nhập Google"):
            st.login()

    else:

        st.success("Đăng nhập thành công")

        st.write("Name:", st.user.get("name"))
        st.write("Email:", st.user.get("email"))

        if st.user.get("picture"):
            st.image(st.user["picture"], width=120)

        st.json(dict(st.user))

        redirect()

        if st.button("Logout"):
            logout()


# =========================
# MAIN
# =========================

def main():

    st.set_page_config(
        page_title="Báo cáo công việc",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    register_navigation_shell()

    user = get_user()

    # =========================
    # LOGIN
    # =========================

    if user is None:

        st.warning("Chưa đăng nhập")

        widget_login()

        st.stop()

    # =========================
    # MODULES
    # =========================

    roles = get_roles(user["email"])

    modules = get_visible_modules(roles)

    if not modules:

        st.error(
            "Không có module phù hợp với tài khoản hiện tại."
        )

        st.stop()

    # =========================
    # ACTIVE MODULE
    # =========================

    active_module = get_module_by_key(
        modules,
        st.session_state.get(
            ACTIVE_MODULE_KEY
        ),
    )

    # HOME
    if active_module is None:

        clear_active_module()

        render_module_home(modules)

        return

    # =========================
    # SIDEBAR
    # =========================

    selected_page = render_function_sidebar(
        active_module
    )
   
    # # =========================
    # # PAGE PERMISSION
    # # =========================

    require_tab(selected_page)

    # # =========================
    # # RUN PAGE
    # # =========================
    
    run_page(selected_page)

# =========================
# START
# =========================

if __name__ == "__main__":
    main()

