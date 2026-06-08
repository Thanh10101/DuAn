import streamlit as st
import qrcode

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
    ImageWin,
)

import win32print
import win32ui


# ======================================
# DANH SÁCH PRINTER
# ======================================

def get_printers():

    try:

        printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL
            | win32print.PRINTER_ENUM_CONNECTIONS
        )

        return [
            printer[2]
            for printer in printers
        ]

    except Exception as e:

        st.error(
            f"Get Printers Error: {e}"
        )

        return []


# ======================================
# TẠO QR WIFI
# ======================================

def generate_wifi_qr(
    ssid,
    password,
):

    try:

        wifi_text = (
            f"WIFI:T:WPA;"
            f"S:{ssid};"
            f"P:{password};;"
        )

        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=2,
        )

        qr.add_data(
            wifi_text
        )

        qr.make(
            fit=True
        )

        img = qr.make_image(
            fill_color="black",
            back_color="white"
        ).convert("RGB")

        return img

    except Exception as e:

        st.error(
            f"Generate QR Error: {e}"
        )

        return None


# ======================================
# TẠO TEM QR
# ======================================

def create_qr_label(
    qr_img,
    ssid,
    password,
    width_px,
    height_px,
):

    try:

        # ======================================
        # PHÓNG TO QR
        # ======================================

        qr_size = int(
            height_px * 0.65
        )

        qr_img = qr_img.resize(
            (qr_size, qr_size),
            Image.Resampling.LANCZOS
        )

        # ======================================
        # LABEL
        # ======================================

        label = Image.new(
            "RGB",
            (width_px, height_px),
            "white"
        )

        draw = ImageDraw.Draw(
            label
        )

        # ======================================
        # FONT
        # ======================================

        try:

            text_font = ImageFont.truetype(
                "arial.ttf",
                int(height_px * 0.055)
            )

        except:

            text_font = ImageFont.load_default()

        # ======================================
        # QR POSITION
        # ======================================

        qr_x = (
            width_px - qr_size
        ) // 2

        #khoảng cách theo tỷ lệ 
        qr_y = int(height_px * 0.03)

        # ======================================
        # KHUNG QR
        # ======================================

        frame_padding = 12

        frame_x1 = qr_x - frame_padding
        frame_y1 = qr_y - frame_padding

        frame_x2 = qr_x + qr_size + frame_padding
        frame_y2 = qr_y + qr_size + frame_padding

        draw.rounded_rectangle(
            [
                (frame_x1, frame_y1),
                (frame_x2, frame_y2),
            ],
            radius=18,
            outline="black",
            width=4,
        )

        # ======================================
        # PASTE QR
        # ======================================

        label.paste(
            qr_img,
            (qr_x, qr_y)
        )

        # ======================================
        # TEXT
        # ======================================

        info_y = frame_y2 + int(height_px * 0.03)

        ssid_text = f"SSID: {ssid}"
        pass_text = f"PASS: {password}"

        # SSID
        ssid_bbox = draw.textbbox(
            (0, 0),
            ssid_text,
            font=text_font
        )

        ssid_width = (
            ssid_bbox[2]
            - ssid_bbox[0]
        )

        draw.text(
            (
                (width_px - ssid_width) // 2,
                info_y
            ),
            ssid_text,
            fill="black",
            font=text_font
        )

        # PASS
        pass_bbox = draw.textbbox(
            (0, 0),
            pass_text,
            font=text_font
        )

        pass_width = (
            pass_bbox[2]
            - pass_bbox[0]
        )

        draw.text(
            (
                (width_px - pass_width) // 2,
                info_y + int(height_px * 0.07)
            ),
            pass_text,
            fill="black",
            font=text_font
        )

        return label

    except Exception as e:

        st.error(
            f"Create Label Error: {e}"
        )

        return None


# ======================================
# IN TEM
# ======================================

def print_qr(
    qr_img,
    ssid,
    password,
    selected_printer,
    quantity,
):

    try:

        LABEL_WIDTH_MM = 50
        LABEL_HEIGHT_MM = 50

        DPI = 300

        MM_TO_INCH = 0.0393701

        label_width_px = int(
            LABEL_WIDTH_MM
            * MM_TO_INCH
            * DPI
        )

        label_height_px = int(
            LABEL_HEIGHT_MM
            * MM_TO_INCH
            * DPI
        )

        # ======================================
        # PRINTER
        # ======================================

        hprinter = win32print.OpenPrinter(
            selected_printer
        )

        hDC = win32ui.CreateDC()

        hDC.CreatePrinterDC(
            selected_printer
        )

        printer_width = hDC.GetDeviceCaps(8)

        printer_height = hDC.GetDeviceCaps(10)

        x1 = int(
            (
                printer_width
                - label_width_px
            ) / 2
        )

        y1 = int(
            (
                printer_height
                - label_height_px
            ) / 2
        )

        x2 = x1 + label_width_px
        y2 = y1 + label_height_px

        # ======================================
        # START PRINT
        # ======================================

        hDC.StartDoc(
            "WiFi QR Print"
        )

        for i in range(quantity):

            label = create_qr_label(
                qr_img=qr_img,
                ssid=ssid,
                password=password,
                width_px=label_width_px,
                height_px=label_height_px,
            )

            if label is None:
                continue

            dib = ImageWin.Dib(
                label.convert("RGB")
            )

            hDC.StartPage()

            dib.draw(
                hDC.GetHandleOutput(),
                (x1, y1, x2, y2)
            )

            hDC.EndPage()

        # ======================================
        # END PRINT
        # ======================================

        hDC.EndDoc()

        hDC.DeleteDC()

        win32print.ClosePrinter(
            hprinter
        )

        st.success(
            "In thành công"
        )

    except Exception as e:

        st.error(
            f"Print QR Error: {e}"
        )


# ======================================
# UI
# ======================================

def widget_wifi_qr():

    try:

        st.set_page_config(
            page_title="QR WIFI",
            layout="wide",
        )

        st.title(
            "📶 In QR WiFi"
        )

        col1, col2 = st.columns(
            [1, 1.5]
        )

        # ======================================
        # LEFT
        # ======================================

        with col1:

            st.subheader(
                "Thông tin WiFi"
            )

            ssid = st.text_input(
                "SSID"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            quantity = st.number_input(
                "Số lượng in",
                min_value=1,
                value=1,
                step=1,
            )

            # ======================================
            # QR MODE
            # ======================================

            qr_mode = st.radio(
                "Chế độ QR",
                [
                    "Tự tạo QR",
                    "Upload QR"
                ]
            )

            qr_img = None

            # ======================================
            # UPLOAD
            # ======================================

            if qr_mode == "Upload QR":

                uploaded_qr = st.file_uploader(
                    "Upload QR Code",
                    type=[
                        "png",
                        "jpg",
                        "jpeg",
                    ]
                )

                if uploaded_qr:

                    qr_img = Image.open(
                        uploaded_qr
                    ).convert("RGB")

            # ======================================
            # AUTO GENERATE
            # ======================================

            else:

                if ssid and password:

                    qr_img = generate_wifi_qr(
                        ssid,
                        password,
                    )

            # ======================================
            # PRINTER
            # ======================================

            printers = get_printers()

            selected_printer = st.selectbox(
                "Chọn máy in",
                printers
            )

            # ======================================
            # PRINT
            # ======================================

            if st.button(
                "🖨️ In QR",
                use_container_width=True
            ):

                if qr_img is None:

                    st.warning(
                        "Vui lòng tạo QR"
                    )

                    st.stop()

                print_qr(
                    qr_img=qr_img,
                    ssid=ssid,
                    password=password,
                    selected_printer=selected_printer,
                    quantity=quantity,
                )

        # ======================================
        # RIGHT
        # ======================================

        with col2:

            st.subheader(
                "Preview Tem"
            )

            if qr_img:

                preview = create_qr_label(
                    qr_img=qr_img,
                    ssid=ssid,
                    password=password,
                    width_px=700,
                    height_px=700,
                )

                if preview:

                    st.image(
                        preview,
                        width=550,
                    )

    except Exception as e:

        st.error(
            f"Widget Error: {e}"
        )


# ======================================
# MAIN
# ======================================

def main():

    try:

        widget_wifi_qr()

    except Exception as e:

        st.error(
            f"Main Error: {e}"
        )


if __name__ == "__main__":
    main()

