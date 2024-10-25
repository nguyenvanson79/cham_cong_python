import mysql.connector
import streamlit as st
import pandas as pd
from io import BytesIO

# Kết nối tới cơ sở dữ liệu MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="cham_cong"
)

# Tạo đối tượng cursor để thực hiện truy vấn SQL
cursor = db.cursor()

# Thực hiện truy vấn để lấy tất cả dữ liệu từ bảng 'attendance'
cursor.execute("SELECT * FROM attendance")
records = cursor.fetchall()

# Đóng kết nối với cơ sở dữ liệu
cursor.close()
db.close()

# Sử dụng Streamlit để hiển thị dữ liệu trên web
st.title("Danh sách Attendance")

# Chuyển dữ liệu thành DataFrame để dễ xử lý
df = pd.DataFrame(records, columns=['ID', 'Tên', 'Thời gian'])

# Bộ lọc theo tên
search_name = st.text_input("Nhập tên để lọc", "")
if search_name:
    df_filtered = df[df['Tên'].str.contains(search_name, case=False, na=False)]
else:
    df_filtered = df

# Hiển thị dữ liệu theo dạng bảng
if not df_filtered.empty:
    st.table(df_filtered)
else:
    st.write("Không có dữ liệu phù hợp.")

# Chức năng xuất file Excel
def to_excel(dataframe):
    output = BytesIO()  # Sử dụng BytesIO để lưu file Excel vào bộ nhớ
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        dataframe.to_excel(writer, sheet_name='Attendance', index=False)
    processed_data = output.getvalue()  # Lấy nội dung của file Excel từ bộ nhớ
    return processed_data

if st.button("Xuất dữ liệu ra Excel"):
    excel_data = to_excel(df_filtered)  # Tạo file Excel
    st.download_button(label="Tải xuống file Excel", data=excel_data, file_name="attendance_data.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
