from tkinter import *
import cv2
import PIL
from PIL import Image, ImageTk
import customtkinter
import os
import time
import login_page as lp
cap = cv2.VideoCapture(0)
state = True
image = None
file = ''


# Show error message in window
def error_message_box(frame, message, color):
    error_label = customtkinter.CTkLabel(frame, text=message, text_color=color, font=('Times New Roman', 20))
    error_label.grid(row=3, column=1)
    frame.after(3500, error_label.destroy)


def get_filename():
    global file
    print(file)
    return file


def has_a_image():
    global file
    if file == '':
        return False
    else:
        return True


def camera_status(root, mode):  # control camera
    global state
    state = mode
    string_var = StringVar()
    string_var.set("")
    font = ('Times New Roman', 20)
    camera_frame = Label(root, width=600, height=440)
    camera_frame.grid(row=1, column=0, columnspan=3)
    camera_button = customtkinter.CTkButton(root, text="Reset Camera", font=font, command=lambda: start_webcam())  # see in the terminal the output message
    camera_button.grid(row=2, column=0, pady=20, padx=15)
    camera_button = customtkinter.CTkButton(root, text="Capture Photo", font=font, command=lambda: stop_webcam())  # see in the terminal the output message
    camera_button.grid(row=2, column=1, pady=20, padx=15)
    camera_button = customtkinter.CTkButton(root, text="Select Photo", font=font, command=lambda: snapshot())
    camera_button.grid(row=2, column=2, pady=20, padx=15)  # see in the terminal the output message
    error_label = customtkinter.CTkLabel(root, textvariable=string_var, font=('Times New Roman', 20))
    error_label.grid(row=3, column=1)

    def stop_webcam():
        global state
        state = False

    def start_webcam():
        global state
        if state is False:
            state = True
            show_frame()

    def snapshot():
        global image, file, state
        image_paths = [os.path.join('Webcam_Snapshots', filename) for filename in os.listdir('Webcam_Snapshots') if
                       filename.lower().endswith(('.png', '.jpg', '.jpeg'))]
        count = len(image_paths) + 1
        print(count)
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
                frame = cv2.flip(frame, 1)
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = PIL.Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                image = img.convert('RGB')
                camera_frame.imgtk = imgtk
                camera_frame.configure(image=imgtk)
                camera_frame.after(1, show_frame)
    if state is True:
        show_frame()



