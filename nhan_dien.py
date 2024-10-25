import cv2
import pickle
import numpy as np
import os
import csv
import time
from datetime import datetime
from sklearn.neighbors import KNeighborsClassifier
from win32com.client import Dispatch
import mysql.connector
import tkinter as tk
from PIL import Image, ImageTk

# Hàm phát âm thông điệp
def speak(message):
    speaker = Dispatch("SAPI.SpVoice")
    speaker.Speak(message)

# Kết nối và tải dữ liệu khuôn mặt từ MySQL
def load_data_from_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="cham_cong"
    )
    cursor = db.cursor()

    # Tải tên người dùng và dữ liệu khuôn mặt
    cursor.execute("SELECT users.name, face_data.face_vector FROM users JOIN face_data ON users.id = face_data.user_id")
    records = cursor.fetchall()

    LABELS = []
    FACES = []

    for name, face_vector in records:
        LABELS.append(name)
        FACES.append(pickle.loads(face_vector))

    cursor.close()
    db.close()

    return np.array(FACES), LABELS

FACES, LABELS = load_data_from_db()

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

# Cột tên cho file CSV
COL_NAMES = ['NAME', 'TIME']

# Hàm lưu thông tin điểm danh
def save_attendance():
    speak("Thank you! You have been noted.")

    # Lấy thời gian hiện tại
    current_time = datetime.now()
    date_str = current_time.strftime("%Y-%m-%d")  # Định dạng ngày
    time_str = current_time.strftime("%H:%M:%S")  # Định dạng giờ
    csv_file_exists = os.path.isfile(f'luu_thoi_gian/luu{date_str}.csv')

    # Ghi thông tin vào CSV
    attendance = [str(detected_name['text']), f"{date_str} {time_str}"]

    with open(f'luu_thoi_gian/luu{date_str}.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not csv_file_exists:
            writer.writerow(COL_NAMES)
        writer.writerow(attendance)

    # Lưu dữ liệu vào MySQL
    save_attendance_to_db(attendance)

# Hàm lưu thông tin điểm danh vào cơ sở dữ liệu
def save_attendance_to_db(attendance):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="cham_cong"
    )
    cursor = db.cursor()

    # Thêm thông tin vào bảng attendance
    insert_query = "INSERT INTO attendance (name, time) VALUES (%s, %s)"
    cursor.execute(insert_query, (attendance[0], attendance[1]))  # Đảm bảo truyền đúng các giá trị

    db.commit()
    cursor.close()
    db.close()

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

def update_video():
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
