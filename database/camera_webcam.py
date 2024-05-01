from tkinter import *
import cv2
import PIL
from PIL import Image, ImageTk
import customtkinter
import os
import database.user_page as up
import face_recognition as fr
import login_page as lp
cap = cv2.VideoCapture(0)

state = True
image = None
camera_frame = None
file = ''


# Show error message in window
def error_message_box(frame, message, color):
    error_label = customtkinter.CTkLabel(frame, text=message, text_color=color, font=('Times New Roman', 20))
    error_label.grid(row=4, column=1)
    frame.after(3500, error_label.destroy)


def get_filename():
    global file
    return file


def set_has_image():
    global file
    file = ''


def has_a_image():
    global file
    if file == '':
        return False
    else:
        return True


def stop_webcam(file_text):
    global state
    state = False
    up.set_filename()
    file_text.config(state='normal')
    file_text.delete("1.0", "end")
    file_text.config(state='disabled')


def start_webcam():
    global state
    if state is False:
        state = True
        show_frame()


def snapshot(root):
    global image, file, state
    image_paths = [os.path.join('../data/Snapshots', filename) for filename in os.listdir('../data/Snapshots') if
                       filename.lower().endswith(('.png', '.jpg', '.jpeg'))]
    count = len(image_paths) + 1
    if state is True:
        error_message_box(root, "Please Capture Photo", 'red')
    elif image is None:
        error_message_box(root, "Error with Webcam please close program and reopen", 'red')
    else:
        error_message_box(root, "Capture Successfully Chosen", 'green')
        image.save(f"Webcam_Snapshots/snapshot_{count}.jpg", 'JPEG')
    file = f"Webcam_Snapshots/snapshot_{count}.jpg"


def show_frame():
    global image
    if state is True:
        ret, frame = cap.read()
        if ret:
            x = 300
            y = 250
            center = (x, y)
            color = (0, 255, 0)
            radius_len = (130, 180)
            frame = cv2.flip(frame, 1)
            chosen_frame = frame
            position_frame = frame

            # chosen image for augmentation
            chosen_cv2image = cv2.cvtColor(chosen_frame, cv2.COLOR_BGR2RGBA)
            # cv2.imshow("", chosen_cv2image)
            chosen_img = PIL.Image.fromarray(chosen_cv2image)
            image = chosen_img.convert('RGB')
            # image showing webcam with facial position
            position_frame = cv2.ellipse(position_frame, center, radius_len, 0, 0, 360, color, 2)
            cv2image = cv2.cvtColor(position_frame, cv2.COLOR_BGR2RGBA)
            img = PIL.Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)

            camera_frame.imgtk = imgtk
            camera_frame.configure(image=imgtk)

            camera_frame.after(1, show_frame)


def camera_status(root, mode, file_text):  # control camera
    global state, camera_frame
    state = mode
    string_var = StringVar()
    string_var.set("")
    font = ('Times New Roman', 20)
    camera_frame = customtkinter.CTkLabel(root, text="Please position your face as closely within the green line as you can.", font=('Times New Roman', 16))
    camera_frame.grid(row=1, column=0, columnspan=3)
    camera_frame = Label(root, width=600, height=440)
    camera_frame.grid(row=2, column=0, columnspan=3)
    camera_button = customtkinter.CTkButton(root, text="Reset Camera", font=font, command=lambda: start_webcam())  # see in the terminal the output message
    camera_button.grid(row=3, column=0, pady=20, padx=15)
    camera_button = customtkinter.CTkButton(root, text="Capture Photo", font=font, command=lambda: stop_webcam(file_text))  # see in the terminal the output message
    camera_button.grid(row=3, column=1, pady=20, padx=15)
    camera_button = customtkinter.CTkButton(root, text="Select Photo", font=font, command=lambda: snapshot(root))
    camera_button.grid(row=3, column=2, pady=20, padx=15)  # see in the terminal the output message
    error_label = customtkinter.CTkLabel(root, textvariable=string_var, font=('Times New Roman', 20))
    error_label.grid(row=4, column=1)

    if state is True:
        show_frame()



