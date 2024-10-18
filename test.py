import tkinter as tk
import subprocess

# Hàm chạy file them_khuan_mat.py
def run_them_khuan_mat():
    subprocess.run(["python", "them_khuan_mat.py"])

# Hàm chạy file nhan_dien.py
def run_nhan_dien():
    subprocess.run(["python", "nhan_dien.py"])

# Tạo giao diện
window = tk.Tk()
window.geometry('500x400')
window.title("Chấm Công Tự Động")

# Tạo tiêu đề chính
label_title = tk.Label(window, text="Chấm Công Tự Động", font=("Arial", 24), fg="blue")
label_title.pack(pady=10)

# Tạo tiêu đề nhóm
label_team = tk.Label(window, text="Nhóm 6", font=("Arial", 16), fg="black")
label_team.pack(pady=5)

# Tạo nút để chạy them_khuan_mat.py
btn_them_khuan_mat = tk.Button(window, text="Thêm khuôn mặt", command=run_them_khuan_mat)
btn_them_khuan_mat.pack(pady=10)

# Tạo nút để chạy nhan_dien.py
btn_nhan_dien = tk.Button(window, text="Bắt Đầu Điểm Danh ", command=run_nhan_dien)
btn_nhan_dien.pack(pady=10)

# Hiển thị cửa sổ
window.mainloop()
