import qrcode
from PIL import Image
from PIL import ImageWin

import win32print
import win32ui

import streamlit as st
from utils.excel_utils import ExcelUtil as ex
from unidecode import unidecode

#giao diện
def widget_display(**kwargs):
    try:
        data = kwargs.get("data")
        search_options = kwargs.get("search_options")

        st.title("In QR hàng loạt")

        #Hiển thị table
        st.dataframe(
                data,
                width='stretch',
                height= 200
        )
        
        selects = st.multiselect(
                "Danh sách máy",
                options=list(search_options.keys()),
                format_func=lambda x: f"{x} : {search_options[x]}"
            )
        
        print_dict = {}
        for machine in selects:
                qty = st.number_input(
                    f"Số lượng in - {machine}",
                    min_value=1,
                    value=1,
                    step=1,
                    key=f"qty_{machine}"
                )
                print_dict[machine] = qty

        return print_dict
    
    except Exception as e:
        raise (f"MES -qr: {e}")
    
def widget_printer(**kwargs):
    try:
        printer_names = kwargs.get("printer_names")

        selected_printer = st.selectbox(
            "Chọn máy in",
            printer_names
        )

        return selected_printer
    
    except Exception as e:
        st.error(f"MES - qr: {e}")
        
def widget_create_qr(**kwargs):
    try:

        qr_data = kwargs.get("qr_data")
        selected_printer = kwargs.get("selected_printer")
        
        if st.button("In QR"):

            LABEL_WIDTH_MM = 50
            LABEL_HEIGHT_MM = 50

            DPI = 203

            MM_TO_INCH = 0.0393701

            label_width_px = int(
                LABEL_WIDTH_MM * MM_TO_INCH * DPI
            )

            label_height_px = int(
                LABEL_HEIGHT_MM * MM_TO_INCH * DPI
            )

            # KẾT NỐI PRINTER
            hprinter = win32print.OpenPrinter(
                selected_printer
            )

            hDC = win32ui.CreateDC()

            hDC.CreatePrinterDC(
                selected_printer
            )

            printer_width = hDC.GetDeviceCaps(8)
            printer_height = hDC.GetDeviceCaps(10)

            x_offset = -10
            y_offset = -10

            x1 = int(
                (printer_width - label_width_px) / 2
            ) + x_offset

            y1 = int(
                (printer_height - label_height_px) / 2
            ) + y_offset

            x2 = x1 + label_width_px
            y2 = y1 + label_height_px

            # START DOC
            hDC.StartDoc("QR Batch Print")

            # LOOP IN
            for qr_text, quantity in qr_data.items():

                for i in range(quantity):

                    label = create_qr_label(
                        qr_text,
                        label_width_px,
                        label_height_px
                    )

                    dib = ImageWin.Dib(label)

                    hDC.StartPage()

                    dib.draw(
                        hDC.GetHandleOutput(),
                        (x1, y1, x2, y2)
                    )

                    hDC.EndPage()

                    st.write(
                        f"Đã in: {qr_text} ({i+1}/{quantity})"
                    )

            # END DOC
            hDC.EndDoc()

            hDC.DeleteDC()

            win32print.ClosePrinter(hprinter)

            st.success("In hoàn tất")

        return selected_printer

    except Exception as e:
        st.error(f"MES - qr: {e}")

#Logic
def display_excel(df):
    try:
        # lấy cột cần dùng
        df_clean = df.dropna(subset=['Mã vạch', 'Tên'], how='any')
        data = df_clean.iloc[:, 2:4]

        machine_options = {
            row.iloc[0]: row.iloc[1]
            for _, row in data.iterrows()
        }

        # tạo dữ liệu search không dấu
        search_options = {
            ma: unidecode(f"{ten}".lower())
            for ma, ten in machine_options.items()
        }
        
        return data,search_options

    except Exception as e:
        raise (f"MES - qr: {e}")

def create_qr_label(data, width_px, height_px):
    try:
        qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=1
        )

        qr.add_data(data)
        qr.make(fit=True)

        qr_img = qr.make_image(
            fill_color="black",
            back_color="white"
        ).convert("RGB")

        qr_size = int(
            min(width_px, height_px) * 0.90
        )

        qr_img = qr_img.resize(
            (qr_size, qr_size),
            Image.Resampling.NEAREST
        )

        # tạo nền
        label = Image.new(
            "RGB",
            (width_px, height_px),
            "white"
        )

        qr_x = (width_px - qr_size) // 2
        qr_y = (height_px - qr_size) // 2

        label.paste(qr_img, (qr_x, qr_y))

        return label
    
    except Exception as e:
        raise (f"MES - qr {e}")

def create_qr():
    try:
        # DANH SÁCH MÁY IN
        printers = win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL
            | win32print.PRINTER_ENUM_CONNECTIONS
        )

        printer_names = [
            printer[2]
            for printer in printers
        ]

        return printer_names

    except Exception as e:
        raise (f"MES -qr: {e}")

def main():

    try:
        # READ EXCEL
        df = ex.read_excel(
            "app/excel/station_data.xlsx"
        )

        # UI CHỌN PRINTER
        selected_printer = widget_printer(
            printer_names = create_qr()
        )

        data, search_options = display_excel(df)
        # UI CHỌN QR
        qr_data = widget_display(
            data = data,
            search_options = search_options
        )

        # IN QR
        widget_create_qr(
            qr_data=qr_data,
            selected_printer=selected_printer
        )

    except Exception as e:
        st.error(f"MES - qr: {e}")


main()
