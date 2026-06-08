import streamlit as st
from streamlit_extras.card_selector import card_selector

from sidebar import open_module
from sidebar import MODULE_CARD_KEY


def render_module_home(modules):
    st.title("Trang chủ")

    selected_index = card_selector(
        [
            {
                "icon": module["icon"],
                "title": module["title"],
                "description": module["description"],
            }
            for module in modules
        ],
        key=MODULE_CARD_KEY,
    )

    if selected_index is not None:
        open_module(modules[selected_index])
        st.rerun()
