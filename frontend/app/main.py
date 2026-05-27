
import streamlit as st
from navigations import create_navigation

st.set_page_config(layout="wide")
create_navigation().run()