import streamlit as st
import pandas as pd
import time
import os
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.chrome import ChromeDriverManager

st.title("MES Data Crawler")

# =========================================
# LOGIN
# =========================================

USERNAME = st.text_input("Username")
PASSWORD = st.text_input(
    "Password",
    type="password"
)

# =========================================
# BUTTON
# =========================================

if st.button("Cào dữ liệu"):

    if not USERNAME or not PASSWORD:

        st.warning("Nhập tài khoản")
        st.stop()

      
    # =====================================
    # CHROME OPTIONS
    # =====================================

    options = Options()

    # TẮT HEADLESS ĐỂ DEBUG
    # options.add_argument("--headless=new")

    options.add_argument("--start-maximized")

    options.add_argument("--disable-gpu")

    options.add_argument("--disable-dev-shm-usage")

    options.add_argument("--no-sandbox")

    # fake browser thật
    options.add_argument(
        "user-agent=Mozilla/5.0"
    )

    # =====================================
    # DRIVER
    # =====================================

    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options
    )

    # timeout lớn hơn
    wait = WebDriverWait(driver, 60)



    # =====================================
    # PROGRESS BAR
    # =====================================

    progress = st.progress(0)

    status = st.empty()

    # =====================================
    # LOGIN PAGE
    # =====================================

    status.write("Đang mở login...")

    driver.get(
        "https://tamatra-fx.digitalfactory.vn/login"
    )

    progress.progress(10)

    # =====================================
    # LOGIN
    # =====================================

    wait.until(
        EC.presence_of_all_elements_located(
            (By.TAG_NAME, "input")
        )
    )

    inputs = driver.find_elements(
        By.TAG_NAME,
        "input"
    )

    inputs[0].send_keys(USERNAME)

    inputs[1].send_keys(PASSWORD)

    buttons = driver.find_elements(
        By.TAG_NAME,
        "button"
    )

    for btn in buttons:

        text = btn.text.strip().lower()

        if (
            "login" in text
            or "đăng nhập" in text
        ):

            btn.click()
            break

    status.write("Đang login...")

    time.sleep(5)

    progress.progress(20)

    # =====================================
    # OPEN PAGE
    # =====================================

    status.write("Đang mở station...")

    driver.get(
        "https://tamatra-fx.digitalfactory.vn/master-data/station"
    )

    # chờ table
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "tbody tr")
        )
    )

    time.sleep(5)

    progress.progress(30)

    # =====================================
    # ĐỔI PAGE SIZE = 100
    # =====================================

    try:

        selects = driver.find_elements(
            By.CSS_SELECTOR,
            ".mud-select-input"
        )

        if selects:

            selects[-1].click()

            time.sleep(1)

            items = driver.find_elements(
                By.CSS_SELECTOR,
                ".mud-list-item"
            )

            for item in items:

                if item.text.strip() == "100":

                    driver.execute_script(
                        "arguments[0].click();",
                        item
                    )

                    break

            time.sleep(3)

    except Exception as e:

        st.warning(e)

    # =====================================
    # GET TOTAL
    # =====================================

    total_pages = 4

    # =====================================
    # CRAWL
    # =====================================

    all_data = []

    page = 1

    while True:

        status.write(
            f"Đang cào page {page}"
        )

        time.sleep(3)

        # =================================
        # JS EXTRACT TABLE
        # =================================

        rows_data = driver.execute_script("""
            let rows = document.querySelectorAll('tbody tr');

            let result = [];

            rows.forEach(row => {

                let cols = row.querySelectorAll('td');

                let rowData = [];

                cols.forEach(col => {
                    rowData.push(col.innerText.trim());
                });

                result.push(rowData);
            });

            return result;
        """)

        # lọc dòng rỗng
        rows_data = [
            r for r in rows_data
            if len(r) > 0
        ]

        all_data.extend(rows_data)

        # =================================
        # PROGRESS
        # =================================

        current_progress = min(
            30 + int((page / total_pages) * 60),
            95
        )

        progress.progress(current_progress)

        status.write(
            f"Đã lấy {len(all_data)} dòng"
        )

        # =================================
        # NEXT PAGE
        # =================================

        try:

            pagination_buttons = driver.find_elements(
                By.CSS_SELECTOR,
                ".mud-table-pagination button"
            )

            if len(pagination_buttons) < 3:

                break

            next_btn = pagination_buttons[2]

            disabled = next_btn.get_attribute(
                "disabled"
            )

            class_name = next_btn.get_attribute(
                "class"
            )

            # trang cuối
            if (
                disabled is not None
                or "disabled" in class_name.lower()
            ):

                break

            driver.execute_script("""
                arguments[0].click();
            """, next_btn)

            page += 1

            time.sleep(5)

        except Exception as e:

            st.error(e)

            break

    # =====================================
    # REMOVE DUPLICATE
    # =====================================

    unique_data = []

    seen = set()

    for row in all_data:

        key = tuple(row)

        if key not in seen:

            seen.add(key)

            unique_data.append(row)

    # =====================================
    # DATAFRAME
    # =====================================

    columns = [
        "Id",
        "Mã",
        "Mã vạch",
        "Tên",
        "Cavity",
        "Phân xưởng",
        "Model máy",
        "Thông tin",
        "Loại công việc chạy",
        "OperationType"
    ]

    # chỉ lấy đúng 10 cột
    clean_data = []

    for row in unique_data:

        if len(row) >= 10:

            clean_data.append(row[:10])

    # tạo dataframe có header luôn
    df = pd.DataFrame(
        clean_data,
        columns=columns
    )

    # =====================================
    # SHOW
    # =====================================

    progress.progress(100)

    status.write("Hoàn tất")

    st.success(
        f"Tổng dòng: {len(df)}"
    )

    st.dataframe(
        df,
        width='stretch'
    )

    # =====================================
    # THƯ MỤC LƯU
    # =====================================

    save_folder = "app/excel"

    os.makedirs(
        save_folder,
        exist_ok=True
    )

    save_path = os.path.join(
        save_folder,
        "station_data.xlsx"
    )

    # =====================================
    # EXPORT EXCEL
    # =====================================

    excel_buffer = BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Station"
        )

        worksheet = writer.sheets["Station"]

        # auto width
        for column in worksheet.columns:

            max_length = 0

            column_letter = column[0].column_letter

            for cell in column:

                try:

                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass

            worksheet.column_dimensions[
                column_letter
            ].width = max_length + 5

    # =====================================
    # LƯU Ổ CỨNG
    # =====================================

    with open(save_path, "wb") as f:

        f.write(excel_buffer.getvalue())

    st.success(
        f"Đã lưu: {save_path}"
    )

    # =====================================
    # DOWNLOAD BUTTON
    # =====================================

    excel_buffer.seek(0)

    st.download_button(
        label="Tải Excel",
        data=excel_buffer,
        file_name="station_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # =====================================
    # CLOSE
    # =====================================

    driver.quit()
