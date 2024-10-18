import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from sklearn.neighbors import KNeighborsClassifier
from win32com.client import Dispatch
import tkinter as tk
from PIL import Image, ImageTk

def speak(message):
    """Sử dụng SAPI để phát âm thông điệp."""
    speaker = Dispatch(("SAPI.SpVoice"))
    speaker.Speak(message)

# Tải dữ liệu khuôn mặt và nhãn đã lưu
with open('data/names.pkl', 'rb') as f:
    LABELS = pickle.load(f)

with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

# Huấn luyện mô hình K-Nearest Neighbors (KNN)
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

# Tạo giao diện Tkinter
window = tk.Tk()
window.title("Nhận diện khuôn mặt")
window.geometry('1000x600')

# Khung chính
main_frame = tk.Frame(window)
main_frame.grid(row=0, column=0, sticky="nsew")

# Khung bên trái để hiển thị tên và nút
left_frame = tk.Frame(main_frame, width=300, height=600)
left_frame.grid(row=0, column=0, padx=10, pady=10)
left_frame.grid_propagate(False)

label_name = tk.Label(left_frame, text="Tên nhận diện:", font=('Arial', 20))
label_name.pack(pady=10)

detected_name = tk.Label(left_frame, text="", font=('Arial', 16), fg='blue')
detected_name.pack(pady=20)

# Tạo nút ghi nhận
def save_attendance():
    speak("Thank you! You have been noted.")
    with open(f'luu_thoi_gian/luu{date}.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not csv_file_exists:
            writer.writerow(COL_NAMES)
        writer.writerow(attendance)

button_save = tk.Button(left_frame, text="Ghi nhận", command=save_attendance, font=('Arial', 16), width=15, height=2)
button_save.pack(pady=20)

# Tạo nút thoát
def quit_program():
    video.release()
    cv2.destroyAllWindows()
    window.destroy()

button_quit = tk.Button(left_frame, text="Thoát", command=quit_program, font=('Arial', 16), width=15, height=2)
button_quit.pack(pady=20)

# Khung bên phải để hiển thị camera
right_frame = tk.Frame(main_frame, width=640, height=480)
right_frame.grid(row=0, column=1, padx=10, pady=10)
right_frame.grid_propagate(False)

label_video = tk.Label(right_frame)
label_video.pack()

# Khởi tạo video từ camera và nạp mô hình nhận diện khuôn mặt
video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/huan_luyen.xml')

# Cột tên cho file CSV
COL_NAMES = ['NAME', 'TIME']

def update_video():
    global attendance, csv_file_exists, date

    ret, frame = video.read()
    if ret:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Chuyển sang ảnh xám
        faces = facedetect.detectMultiScale(gray, 1.3, 5)  # Nhận diện khuôn mặt

        for (x, y, w, h) in faces:
            # Cắt và thay đổi kích thước khuôn mặt
            crop_img = frame[y:y+h, x:x+w]
            resized_img = cv2.resize(crop_img, (50, 50)).flatten().reshape(1, -1)

            # Dự đoán nhãn (tên) bằng KNN
            output = knn.predict(resized_img)

            # Hiển thị tên dự đoán lên giao diện Tkinter
            detected_name.config(text=str(output[0]))

            # Lấy thời gian hiện tại
            current_time = time.time()
            date = datetime.fromtimestamp(current_time).strftime("%d-%m-%Y")
            time_str = datetime.fromtimestamp(current_time).strftime("%H:%M:%S")
            csv_file_exists = os.path.isfile(f'luu_thoi_gian/luu{date}.csv')

            # Ghi thông tin khuôn mặt vào CSV
            attendance = [str(output[0]), f"{date} {time_str}"]

            # Vẽ khung hình quanh khuôn mặt
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.rectangle(frame, (x, y-40), (x+w, y), (50, 50, 255), -1)
            cv2.putText(frame, str(output[0]), (x, y-15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

        # Hiển thị khung hình camera trên giao diện
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        label_video.imgtk = imgtk
        label_video.configure(image=imgtk)

    window.after(10, update_video)  # Cập nhật mỗi 10ms

# Chạy hàm cập nhật video
update_video()

# Chạy ứng dụng Tkinter
window.mainloop()
