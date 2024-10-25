import cv2
import pickle
import numpy as np
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector

# Khởi tạo danh sách để lưu trữ dữ liệu khuôn mặt và các biến toàn cục
faces_data = []
frame_count = 0
user_name = ""


# Kết nối tới cơ sở dữ liệu MySQL
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="cham_cong"
    )


# Hàm bắt đầu quá trình ghi lại khuôn mặt
def start_capture():
    global user_name, faces_data, frame_count
    user_name = entry_name.get().strip()

    if not user_name:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên của bạn.")
        return

    # Mở camera
    video_capture = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier('data/huan_luyen.xml')

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, 1.3, 5)

        for (x, y, w, h) in faces:
            face_crop = frame[y:y + h, x:x + w]
            resized_face = cv2.resize(face_crop, (50, 50))

            if len(faces_data) < 50 and frame_count % 10 == 0:
                faces_data.append(resized_face)

            frame_count += 1

            # Vẽ hình chữ nhật và hiển thị số lượng khuôn mặt đã thu thập
            cv2.putText(frame, str(len(faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (50, 50, 255), 1)

        # Hiển thị khung hình trên giao diện
        display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        display_image = Image.fromarray(display_frame)
        imgtk = ImageTk.PhotoImage(image=display_image)
        label_video.imgtk = imgtk
        label_video.configure(image=imgtk)

        window.update()

        # Điều kiện dừng: Nhấn 'q' hoặc thu thập đủ 100 khuôn mặt
        if cv2.waitKey(1) & 0xFF == ord('q') or len(faces_data) == 50:
            break

    video_capture.release()
    cv2.destroyAllWindows()
    save_face_data()


# Hàm lưu dữ liệu khuôn mặt vào MySQL
def save_face_data():
    global faces_data, user_name
    faces_data = np.asarray(faces_data).reshape(50, -1).tolist()

    try:
        db = connect_db()
        cursor = db.cursor()

        # Kiểm tra nếu người dùng đã tồn tại, nếu không thêm vào
        cursor.execute("SELECT id FROM users WHERE name = %s", (user_name,))
        result = cursor.fetchone()

        if result is None:
            cursor.execute("INSERT INTO users (name) VALUES (%s)", (user_name,))
            db.commit()
            user_id = cursor.lastrowid
        else:
            user_id = result[0]

        # Lưu dữ liệu khuôn mặt
        for face_data in faces_data:
            cursor.execute(
                "INSERT INTO face_data (user_id, face_vector) VALUES (%s, %s)",
                (user_id, pickle.dumps(face_data))
            )

        db.commit()
        messagebox.showinfo("Thành công", "Dữ liệu khuôn mặt đã được lưu.")
    except mysql.connector.Error as err:
        messagebox.showerror("Lỗi", f"Lỗi khi lưu vào CSDL: {err}")
    finally:
        cursor.close()
        db.close()


# Tạo giao diện người dùng với Tkinter
window = tk.Tk()
window.title("Thu thập ảnh chấm công")
window.geometry('600x600')

# Cấu hình lưới để căn giữa
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)

# Khung chính chứa tất cả phần tử
main_frame = tk.Frame(window)
main_frame.grid(row=0, column=0, sticky="nsew")

# Cấu hình khung chính để căn giữa
main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure([0, 1, 2], weight=1)

# Khung video hiển thị hình ảnh từ camera
label_video = tk.Label(main_frame)
label_video.grid(row=0, column=0, pady=10, padx=10)

# Khung nhập tên và nút bắt đầu
frame_input = tk.Frame(main_frame)
frame_input.grid(row=1, column=0, pady=10, padx=10)

label_name = tk.Label(frame_input, text="Nhập tên của bạn:")
label_name.pack(pady=5)

entry_name = tk.Entry(frame_input)
entry_name.pack(pady=5)

button_start = tk.Button(frame_input, text="Bắt đầu", command=start_capture)
button_start.pack(pady=5)

# Chạy ứng dụng Tkinter
window.mainloop()
