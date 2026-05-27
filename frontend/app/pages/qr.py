import os
import re
import qrcode
import streamlit as st


def safe_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", name)



def input_list(text):
    return [x.strip() for x in re.split(r'[\s,]+', text) if x.strip()]


def main():
    st.title("Tạo QR hàng loạt")
    folder = "image/"
    folder += st.text_input("Nhập tên thư mục cần tạo:")
    
    data_input = st.text_area(
        "Nhập dữ liệu (mỗi dòng 1 QR)",
        height=300
    )

    if st.button("Tạo QR"):
        if not folder:
            st.warning("Chưa nhập nhập thư mục cần lưu")
            return
        
        os.makedirs(str(folder), exist_ok=True)

        data = input_list(data_input)

        if not data:
            st.warning("Chưa nhập dữ liệu")
            return

        for item in data:
            filename = safe_filename(item)

            img = qrcode.make(item)

            save_path = os.path.join(folder, f"{filename}.png")
            img.save(save_path)

            st.write(f"Đã tạo: {save_path}")

        st.success(f"Hoàn tất! Đã tạo {len(data)} QR trong thư mục '{folder}'")


if __name__ == "__main__":
    main()