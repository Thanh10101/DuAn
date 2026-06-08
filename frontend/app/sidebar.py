import streamlit as st

from module import get_page_by_file


ACTIVE_MODULE_KEY = "active_module_key"
ACTIVE_PAGE_KEY = "active_page_file"
MODULE_CARD_KEY = "module_cards"


def clear_active_module(clear_module_card=False):
    st.session_state.pop(ACTIVE_MODULE_KEY, None)
    st.session_state.pop(ACTIVE_PAGE_KEY, None)

    if clear_module_card:
        st.session_state.pop(MODULE_CARD_KEY, None)


def open_module(module):
    st.session_state[ACTIVE_MODULE_KEY] = module["key"]
    st.session_state[ACTIVE_PAGE_KEY] = module["pages"][0]["file"]


def render_function_sidebar(module):
    page_files = [page["file"] for page in module["pages"]]

    if st.session_state.get(ACTIVE_PAGE_KEY) not in page_files:
        st.session_state[ACTIVE_PAGE_KEY] = page_files[0]

    with st.sidebar:
        if st.button("Trang chủ", icon=":material/home:"):
            clear_active_module(clear_module_card=True)
            st.rerun()

        st.divider()
        st.caption("Module")
        st.subheader(module["title"])
        st.caption(module["description"])
        st.divider()

        selected_file = st.radio(
            "Chức năng",
            options=page_files,
            format_func=lambda page_file: get_page_by_file(module, page_file)["title"],
            key=ACTIVE_PAGE_KEY,
        )

    return get_page_by_file(module, selected_file)
