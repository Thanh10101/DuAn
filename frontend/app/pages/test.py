import streamlit as st
import qrcode
from PIL import Image
from io import BytesIO
import zipfile
import os
import re

def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)


st.title("Tạo mã QR")

text_input = st.text_area(
    "Nhập dữ liệu (mỗi dòng là 1 QR)",
    height=200
)

option = st.radio(
    "Kiểu lưu",
    [
        "Lưu tại máy chủ",
        "Tải về máy người dùng"
    ]
)

folder = "qr_output"

if st.button("Tạo QR"):

    data = [x.strip() for x in text_input.splitlines() if x.strip()]

    if not data:
        st.warning("Chưa nhập dữ liệu")
        st.stop()

    os.makedirs(folder, exist_ok=True)

    zip_buffer = BytesIO()

    with zipfile.ZipFile(zip_buffer, "w") as zip_file:

        for item in data:

            filename = safe_filename(item)

            # Tạo QR
            img = qrcode.make(item)

            # Convert ảnh sang bytes
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)
            # Convert sang PIL Image thật
            img = img.get_image()
            # ======================
            # HIỂN THỊ PREVIEW QR
            # ======================

            st.subheader(item)

            col1, col2 = st.columns([1, 2])

            with col1:
                st.image(img, width=200)

            with col2:

                # ======================
                # TẢI TỪNG QR
                # ======================

                st.download_button(
                    label=f"Tải {filename}.png",
                    data=buffer.getvalue(),
                    file_name=f"{filename}.png",
                    mime="image/png"
                )

            # ======================
            # LƯU MÁY CHỦ
            # ======================

            if option == "Lưu tại máy chủ":

                save_path = os.path.join(
                    folder,
                    f"{filename}.png"
                )

                img.save(save_path)

                st.success(f"Đã lưu: {save_path}")

            # ======================
            # THÊM VÀO FILE ZIP
            # ======================

            zip_file.writestr(
                "qr.png",
                buffer.getvalue()
            )

    # ======================
    # TẢI TẤT CẢ ZIP
    # ======================

    buffer.seek(0)

    st.divider()

    st.download_button(
        label="Tải QR",
        data=buffer.getvalue(),
        file_name="qr.png",
        mime="image/png"
    )

    st.success(f"Hoàn tất! Đã tạo {len(data)} QR")
