import pandas as pd
import streamlit as st
from pathlib import Path
import re


# =========================================
# 🔧 HÀM XỬ LÝ HEADER CHUNG
# =========================================
def clean_header(df, header_row_index, name):
    df.columns = df.iloc[header_row_index]
    df = df.iloc[header_row_index + 1:].reset_index(drop=True)

    # Fix cột NaN / Unnamed
    new_cols = []
    for i, col in enumerate(df.columns):
        if pd.isna(col) or "Unnamed" in str(col):
            new_cols.append(df.iloc[0, i])
        else:
            new_cols.append(col)

    df.columns = new_cols

    # Drop dòng dùng để fill header
    df = df.iloc[1:].reset_index(drop=True)

    # Clean tên cột (rất quan trọng)
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )

    # Xóa dòng NaN theo cột chính
    if name in df.columns:
        df = df.dropna(subset=[name])
    else:
        print(f"⚠️ Không tìm thấy cột '{name}'")

    return df.reset_index(drop=True)


# =========================================
# 🔥 HÀM CHỌN CỘT
# =========================================
def select_columns(df, cols):
    cols = [c for c in cols if c in df.columns]
    return df[cols]


def normalize_employee_value(value):
    if pd.isna(value):
        return ""

    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    parts = [part.strip() for part in re.split(r"[\n,;/|]+", text) if part.strip()]
    parts = sorted(parts, key=str.casefold)
    return " | ".join(parts)


def add_employee_columns(df, source_columns, output_column):
    source_column = next((column for column in source_columns if column in df.columns), None)

    if source_column is None:
        df[output_column] = ""
        df["Nhân viên_key"] = ""
        return df

    df[output_column] = df[source_column]
    df["Nhân viên_key"] = df[source_column].apply(normalize_employee_value)
    return df


# =========================================
# 🔥 HÀM TẠO BẢNG VÀ CĂN LỀ
# =========================================
def format_sheet(df, writer, sheet_name):
    # Ghi vào excel
    df.to_excel(writer, sheet_name=sheet_name, index=False)

    worksheet = writer.sheets[sheet_name]

    df.columns = make_unique_columns(df.columns)

    for i, col in enumerate(df.columns):
        column_data = df[col]

        # Nếu bị trùng cột → lấy cột đầu
        if isinstance(column_data, pd.DataFrame):
            column_data = column_data.iloc[:, 0]

        max_len = column_data.fillna("").astype(str).str.len().max()
        max_len = max(max_len, len(str(col))) + 2

        worksheet.set_column(i, i, max_len)

    # Tạo bảng (Table) trong Excel
    max_row, max_col = df.shape
    if max_row > 0 and max_col > 0:
        column_settings = [{"header": column} for column in df.columns]
        worksheet.add_table(0, 0, max_row, max_col - 1, {
            "columns": column_settings,
            "style": "Table Style Medium 9",
        })

    st.code(f"\nĐã tạo sheet '{sheet_name}' thành công!")


# =========================================
# 🔥 ĐỔI TÊN CỘT TRÙNG
# =========================================
def make_unique_columns(columns):
    seen = {}
    new_cols = []

    for col in columns:
        if col not in seen:
            seen[col] = 0
            new_cols.append(col)
        else:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")

    return new_cols


def main():
    try:
            # =========================================
        # 📥 ĐỌC FILE
        # =========================================
        base_dir = Path(__file__).parent
        
        thong_ke =  st.file_uploader("Thong ke", type=["xls", "xlsx"])
        phieu_luong =  st.file_uploader("Phieu luong", type=["xls", "xlsx"])
    

        if st.button("thêm"):
            df_thong_ke = pd.read_excel(thong_ke, header=None)
            df_phieu_luong = pd.read_excel(phieu_luong, header=None)

            # =========================================
            # 🔄 XỬ LÝ HEADER
            # =========================================
            df_thong_ke = clean_header(df_thong_ke, 5, "Kế hoạch sản xuất")
            df_phieu_luong = clean_header(df_phieu_luong, 3, "Phiếu thống kê")

            df_thong_ke.columns = make_unique_columns(df_thong_ke.columns)
            df_phieu_luong.columns = make_unique_columns(df_phieu_luong.columns)

            print(df_phieu_luong.columns)
            print(df_thong_ke.columns)

            # =========================================
            # 🔧 CHUẨN HÓA DỮ LIỆU TRƯỚC MERGE
            # =========================================

            # Chuẩn hóa số
            df_phieu_luong["Số lượng (kg)"] = pd.to_numeric(df_phieu_luong["Số lượng (kg)"], errors="coerce")
            df_phieu_luong["Số lượng TC (kg)"] = pd.to_numeric(df_phieu_luong["Số lượng TC (kg)"], errors="coerce")

            # Tạo cột so sánh
            df_phieu_luong["Số lượng 1"] = (
                df_phieu_luong["Số lượng"].fillna(0)
                + df_phieu_luong["Số lượng TC nhập"].fillna(0)
            )

            df_thong_ke = add_employee_columns(
                df_thong_ke,
                ["Nhân viên", "Danh sách nhân viên"],
                "Nhân viên_thống_kê",
            )
            df_phieu_luong = add_employee_columns(
                df_phieu_luong,
                ["Danh sách nhân viên", "Nhân viên"],
                "Nhân viên_phiếu_lượng",
            )

            # Đồng bộ tên cột
            df_phieu_luong["Mã hàng"] = df_phieu_luong["Sản phẩm"]
            df_phieu_luong["Số thống kê"] = df_phieu_luong["Phiếu thống kê"]

            # =========================================
            # 🔢 TẠO IDX
            # =========================================
            idx_group_keys = ["Mã hàng", "Số lượng 1", "Số thống kê", "Nhân viên_key"]

            df_thong_ke = df_thong_ke.sort_values(
                by=idx_group_keys,
                kind="mergesort",
            ).reset_index(drop=True)

            df_phieu_luong = df_phieu_luong.sort_values(
                by=idx_group_keys,
                kind="mergesort",
            ).reset_index(drop=True)

            df_thong_ke["idx"] = df_thong_ke.groupby(idx_group_keys).cumcount()
            df_phieu_luong["idx"] = df_phieu_luong.groupby(idx_group_keys).cumcount()

            # =========================================
            # 🔗 MERGE SO SÁNH
            # =========================================
            merge_keys = [
                "Mã hàng",
                "Số lượng 1",
                "Số thống kê",
                "idx",
                "Nhân viên_key",
            ]

            merged = pd.merge(
                df_thong_ke,
                df_phieu_luong,
                on=merge_keys,
                how="outer",
                indicator=True,
            )

            # =========================================
            # 📊 PHÂN LOẠI KẾT QUẢ
            # =========================================
            duplicates = merged[merged["_merge"] == "both"].copy()
            only_thong_ke = merged[merged["_merge"] == "left_only"].copy()
            only_phieu_luong = merged[merged["_merge"] == "right_only"].copy()

            # Thêm cột ghi chú cho các bản ghi chỉ có 1 bên
            def detect_mismatch_reason(row, other_df):
                try:
                    mh = row.get("Mã hàng")
                    stt = row.get("Số thống kê")
                    qty = row.get("Số lượng 1")
                    emp = row.get("Nhân viên_key", "")
                except Exception:
                    return ""

                mask = (other_df.get("Mã hàng") == mh) & (other_df.get("Số thống kê") == stt)
                if not mask.any():
                    return "Không có trong file kia"

                # Nếu tồn tại cùng Mã hàng + Số thống kê với cùng Số lượng => khác nhân viên
                same_qty = other_df[mask & (other_df.get("Số lượng 1") == qty)]
                if not same_qty.empty:
                    return "sai cột nhân viên"

                # Nếu tồn tại cùng Mã hàng + Số thống kê với cùng Nhân viên_key => khác số lượng
                same_emp = other_df[mask & (other_df.get("Nhân viên_key") == emp)]
                if not same_emp.empty:
                    return "sai cột số lượng"

                # Mismatch khác
                return "sai cột số lượng"

            only_thong_ke["Ghi chú"] = only_thong_ke.apply(lambda r: detect_mismatch_reason(r, df_phieu_luong), axis=1)
            only_phieu_luong["Ghi chú"] = only_phieu_luong.apply(lambda r: detect_mismatch_reason(r, df_thong_ke), axis=1)

            # =========================================
            # 💾 XUẤT FILE EXCEL
            # =========================================
            output_file = base_dir / "ket_qua_so_sanh.xlsx"

            if output_file.exists():
                try:
                    output_file.unlink()
                except PermissionError:
                    st.error("Hãy đóng file ket_qua_so_sanh.xlsx trước khi xuất lại.")
                    return

            cols_keep = [
                "Số thống kê",
                "Lệnh sản xuất",
                "Mã hàng",
                "Số lượng 1",
                "idx",
                "Nhân viên_key",
                "Nhân viên_thống_kê",
                "Nhân viên_phiếu_lượng",
                "Ghi chú",
                "_merge",
            ]

            duplicates = select_columns(duplicates, cols_keep)
            only_thong_ke = select_columns(only_thong_ke, cols_keep)
            only_phieu_luong = select_columns(only_phieu_luong, cols_keep)

            # Sắp xếp theo số lượng
            only_phieu_luong.sort_values(by=["Số lượng 1"], ascending=[True], inplace=True)
            only_thong_ke.sort_values(by=["Số lượng 1"], ascending=[True], inplace=True)

            with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
                format_sheet(duplicates, writer, "Trung")
                format_sheet(only_thong_ke, writer, "KhongCoTrong_PhieuLuong")
                format_sheet(only_phieu_luong, writer, "KhongCoTrong_ThongKe")
                format_sheet(df_thong_ke, writer, "Thong_ke")
                format_sheet(df_phieu_luong, writer, "Phieu_luong")

            # Hiển thị dataframe
            st.write("Dữ liệu thống kê của bạn:", only_thong_ke)
            st.write("Dữ liệu phiếu lương của bạn:", only_phieu_luong)
    except Exception as e:
        st.warning(f"check - {e}")

main()
