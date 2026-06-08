import streamlit as st
import google.generativeai as genai

from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()
secret_key = os.getenv("GEMINI_SECRET_KEY")
# ======================================
# GEMINI API
# ======================================


genai.configure(
    api_key = secret_key
)

# ======================================
# GEMINI API
# ======================================

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


# ======================================
# PAGE
# ======================================

st.set_page_config(
    page_title="Gemini Vision Chat",
    layout="wide",
)

st.title("🤖 Gemini Vision Chat")


# ======================================
# MEMORY
# ======================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ======================================
# HIỂN THỊ CHAT
# ======================================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.markdown(
            msg["content"]
        )


# ======================================
# UPLOAD IMAGE
# ======================================

uploaded_image = st.file_uploader(
    "Upload ảnh",
    type=[
        "png",
        "jpg",
        "jpeg"
    ]
)


# ======================================
# SHOW IMAGE
# ======================================

image = None

if uploaded_image:

    image = Image.open(
        uploaded_image
    )

    st.image(
        image,
        caption="Ảnh đã upload",
        width=300
    )


# ======================================
# CHAT INPUT
# ======================================

prompt = st.chat_input(
    "Nhập câu hỏi..."
)


# ======================================
# USER MESSAGE
# ======================================

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    with st.chat_message("user"):

        st.markdown(prompt)

    # ======================================
    # AI RESPONSE
    # ======================================

    with st.chat_message("assistant"):

        with st.spinner("AI đang xử lý..."):

            try:

                # ======================================
                # IMAGE + PROMPT
                # ======================================

                if image:

                    response = model.generate_content(
                        [
                            prompt,
                            image
                        ]
                    )

                # ======================================
                # TEXT ONLY
                # ======================================

                else:

                    response = model.generate_content(
                        prompt
                    )

                answer = response.text

            except Exception as e:

                answer = f"Lỗi: {e}"

            st.markdown(answer)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

