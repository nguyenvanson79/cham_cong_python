import tkinter as tk
import os
import subprocess
import sys

# Hàm chung để chạy file Python
def run_file(filename, is_streamlit=False):
    if os.path.exists(filename):
        if is_streamlit:
            # Chạy file bằng Streamlit
            subprocess.Popen(["streamlit", "run", filename])
        else:
            # Chạy file bình thường bằng Python
            subprocess.Popen([sys.executable, filename])
    else:
        print(f"File {filename} không tồn tại trong thư mục hiện tại.")

# Tạo giao diện chính bằng Tkinter
main_window = tk.Tk()
main_window.title("Hệ thống quản lý nhận diện khuôn mặt")
main_window.geometry("400x300")

# Nút Nhận diện
btn_recognition = tk.Button(main_window, text="Nhận diện", font=("Arial", 16), command=lambda: run_file("nhan_dien.py"))
btn_recognition.pack(pady=10)

# Nút Thêm khuôn mặt
btn_add_face = tk.Button(main_window, text="Thêm khuôn mặt", font=("Arial", 16), command=lambda: run_file("them_khuan_mat.py"))
btn_add_face.pack(pady=10)

# Nút Web dữ liệu (sử dụng Streamlit)
btn_web_data = tk.Button(main_window, text="Web dữ liệu", font=("Arial", 16), command=lambda: run_file("web_du_lieu.py", is_streamlit=True))
btn_web_data.pack(pady=10)

# Nút Thoát
btn_exit = tk.Button(main_window, text="Thoát", font=("Arial", 16), command=main_window.destroy)
btn_exit.pack(pady=10)

# Chạy giao diện
main_window.mainloop()
