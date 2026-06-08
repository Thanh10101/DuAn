import streamlit as st
from utils.qr_utils import QrUtils as qr

def main():
    try:
        option =  st.radio(
            label="Chọn cách lưu",
            options=("Lưu tại máy chủ", "Lưu tại máy con", "Xem mã qr"),
            index=0  # (Tùy chọn) Vị trí lựa chọn mặc định, bắt đầu từ 0
        )

        data_input = st.text_area(
            "Nhập dữ liệu (mỗi dòng 1 QR)",
            height=200
        )

        match option:
            case "Lưu tại máy chủ":
                folder_name = st.text_input("Nhập tên thư mục cần tạo:")

                folder = "app/image/" + folder_name if folder_name else None

                if st.button("thêm"):
                    st.success(qr.SaveServer(folder = folder, input = data_input))

            case "Lưu tại máy con":
                if st.button("Lưu"):
                    qr.SaveClient(input = data_input)

            case "Xem mã qr":
                if st.button("Xem"):
                    cols = st.columns(2)
                    for i, (key, img) in enumerate(qr.SawQr(data_input).items()):
                        with cols[i % 2]:
                            with cols[i % 2]:

                                st.divider()

                                st.markdown(
                                    f"<h2 style='text-align:center'>{key}</h2>",
                                    unsafe_allow_html=True
                                )

                                #Dùng để căn giữa column
                                left, center, right = st.columns([1,2,1])
                                with center:
                                    st.image(
                                        img.get_image(),
                                        width=350
                                    )

    except Exception as e:
        st.warning(f"Lỗi {e}")


main()
