import runpy
from pathlib import Path

import streamlit as st


APP_DIR = Path(__file__).resolve().parent


def register_navigation_shell():
    st.navigation(
        [st.Page(lambda: None, title="App", default=True)],
        position="hidden",
    ).run()


def run_page(page):
    runpy.run_path(
        str(APP_DIR / page["file"]),
        run_name="__main__",
    )
