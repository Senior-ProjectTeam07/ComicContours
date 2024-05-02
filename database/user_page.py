# user_page.py

import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
import os.path
import database.database_page as cd
import database.login_page as lp
import database.about_page as about
from database.camera_webcam import get_filename, has_a_image, start_webcam, camera_status
import landmarking.landmark as fl
import augmentation.augment as af
from tkinter import *
from tkinter import filedialog
import customtkinter
import shutil
from PIL import Image, ImageTk

filename, label, vid = '', '', ''

def open_database(wind, frame):
    lp.clear_frame(frame)
    cd.main(wind, frame)

def open_login(wind, frame):
    lp.clear_frame(frame)
    lp.create_main_page(wind, frame)

def open_about(wind, frame):
    lp.clear_frame(frame)
    about.main(wind, frame)

# Show error message in window
def message_box(frame, message, color, row, column, columnspan):
    error_label = customtkinter.CTkLabel(frame, text=message, text_color=color, font=('Times New Roman', 20))
    if columnspan == 0:
        error_label.grid(row=row, column=column)
    else:
        error_label.grid(row=row, column=column, columnspan=columnspan)
    frame.after(3500, error_label.destroy)

def set_filename():
    global filename
    filename = ''

def browse_files(text):
    global filename
    filename = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=[("JPG", "*.jpg "),
                                                                                                ("JPEG", "*.jpeg")])
    if has_a_image() is True:
        start_webcam()
    text.config(state='normal')
    text.insert(INSERT, filename)
    text.config(state='disabled')

def create_caricature(frame, aug_frame, checked, text_box, button):
    button['state'] = 'disabled'
    global filename
    fname = filename
    fname = check_snapshot(fname, text_box)
    #  copy image
    if (fname == '') and (checked is False):
        message_box(frame, 'Error: Please upload an image!', 'red', 4, 0, 0)
        message_box(frame, 'Error: Please check consent box!', 'red', 4, 1, 0)
    elif fname == '':
        message_box(frame, 'Error: Please upload an image!', 'red', 4, 0, 2)
    elif checked is False:
        message_box(frame, 'Error: Please check consent box!', 'red', 4, 0, 2)
    if not(fname == '') and (checked is True):
        folder = os.path.abspath("../data/original_images")
        shutil.copy(fname, folder)
        folder = os.path.abspath("../data/Snapshots")
        shutil.copy(fname, folder)
        text_box.config(state='normal')
        text_box.delete("1.0", "end")
        text_box.config(state='disabled')
        filename = ''
        # call facial landmarking to update processed photo folder
        fl.main()
        af.augment_image()
        error_label = customtkinter.CTkLabel(frame, text="Successfully Created Caricature!", text_color="green", font=('Times New Roman', 20))
        error_label.grid(row=4, column=0, columnspan=2)
        frame.after(3500, error_label.destroy)
        show_images_frame(aug_frame, frame, ('Times New Roman', 20), fname)
        aug_frame.tkraise()
    button['state'] = 'normal'

def get_main_frame(frame, main_frame):
    lp.clear_frame(frame)
    frame.destroy()
    main_frame.tkraise()

def check_snapshot(filename, file_text):
    if (filename == '') and (file_text.get(1.0, "end-1c") == '') and (has_a_image()):
        filename = get_filename()
        return filename
    else:
        return filename

def webcam_view(frame1, file_text):
    frame1.after(1, camera_status(frame1, True, file_text))

def show_images_frame(frame, main_frame, font, file):
    # Make a label for the window
    frame_width, frame_height = main_frame.winfo_width(), main_frame.winfo_height()
    frame1 = customtkinter.CTkFrame(master=frame, width=frame_width, height=800)
    frame1.grid(row=0, column=0, columnspan=2, padx=80, pady=80)
    frame1.columnconfigure(index=0, weight=1)
    frame1.rowconfigure(index=1, weight=1)
    customtkinter.CTkLabel(frame1, text="Welcome to Facial Feature Augmentation", font=font).grid(row=0,
                                                                                                  column=0,
                                                                                                  columnspan=2,
                                                                                                  pady=60)
    if not(file == ''):
        label = Label(frame1, width=550, height=400)
        image = Image.open(file)
        img = image.resize((550, 400))
        imgtk = ImageTk.PhotoImage(img)
        label.imgtk = imgtk
        label.configure(image=imgtk)
        label.grid(row=1, column=0, padx=5, pady=60)
        newfile = f"../data/augmented_images/augmented_{os.path.basename(file)}"
        aug_image = Label(frame1, width=550, height=400)
        image = Image.open(newfile)
        img = image.resize((550, 400))
        imgtk = ImageTk.PhotoImage(img)
        aug_image.imgtk = imgtk
        aug_image.configure(image=imgtk)
        aug_image.grid(row=1, column=1, padx=5, pady=60)
        # newfile2 = f"../data/caricature_images/caricature_{os.path.basename(file)}"
        newfile2 = f"../data/caricature_images/bj_novak.jpeg"
        car_image = Label(frame1, width=550, height=400)
        image = Image.open(newfile2)
        img = image.resize((550, 400))
        imgtk = ImageTk.PhotoImage(img)
        car_image.imgtk = imgtk
        car_image.configure(image=imgtk)
        car_image.grid(row=1, column=3, padx=5, pady=60)

    # Liability button
    customtkinter.CTkButton(frame1, text='Return to main Page', font=font, command=lambda: get_main_frame(frame1, main_frame)).grid(row=2, column=1, columnspan=2)

def show_main_page_frame(frame, img_frame, font):
    # Make a label for the window
    frame1 = customtkinter.CTkFrame(master=frame)
    frame1.grid(row=0, column=0, columnspan=2, pady=20)
    customtkinter.CTkLabel(frame1, text="Welcome to Facial Feature Augmentation", font=font).grid(row=0, column=1)

    # Show the created Box
    frame2 = customtkinter.CTkFrame(master=frame)
    frame2.grid(row=1, column=0, columnspan=2, padx=80)
    button = customtkinter.CTkButton(frame2, text='Upload Image', font=font, command=lambda: browse_files(file_text))
    button.pack(pady=12, padx=10, side=LEFT)
    file_text = Text(frame2, height=1, width=100, state='disabled')
    file_text.pack(pady=12, padx=10, side=LEFT)
    # Make a button for browsing images the window
    webcam_view(frame1, file_text)
    # Liability button
    frame3 = customtkinter.CTkFrame(master=frame)
    frame3.grid(row=2, column=0, columnspan=2, pady=20, padx=10)
    checkbutton_var = BooleanVar()
    customtkinter.CTkCheckBox(frame3, text='I consent to having the photo and caricature added to a database for facial recognition research purposes only.',
                              variable=checkbutton_var, font=('Times New Roman', 15)).pack(pady=12, padx=10, side=BOTTOM)

    # Caricature button
    button = customtkinter.CTkButton(frame, text='Create Caricature', font=font, command=lambda: create_caricature(frame, img_frame, checkbutton_var.get(), file_text, button))
    button.grid(row=3, column=0, columnspan=2)
    string_var = StringVar()
    error_label = customtkinter.CTkLabel(frame, textvariable=string_var, font=('Times New Roman', 20))
    error_label.grid(row=4, column=1, columnspan=2)

# Create user window
def main(window, frame):
    font = ('Times New Roman', 20)
    mb = Menu(window)
    mb_dropdown = Menu(mb, tearoff=0)
    mb_dropdown.add_command(label="Logout", font=('Times New Roman', 20), command=lambda: open_login(window, frame))
    mb_dropdown.add_command(label="About", font=('Times New Roman', 20), command=lambda: open_about(window, frame))
    mb_dropdown.add_command(label="Database", font=('Times New Roman', 20), command=lambda: open_database(window, frame))
    mb.add_cascade(label="Menu", menu=mb_dropdown)
    window.config(menu=mb)
    main_frame = customtkinter.CTkFrame(frame)
    image_frame = customtkinter.CTkFrame(frame)
    show_main_page_frame(main_frame, image_frame, font)
    show_images_frame(image_frame, main_frame, font, file='')
    main_frame.grid(row=0, column=0)
    image_frame.grid(row=0, column=0)
    main_frame.tkraise()
    # image_frame.tkraise()
    # Run forever
    window.mainloop()

if __name__ == "__main__":
    # database
    lp.make_user_database()
    # create window
    window = customtkinter.CTk()
    customtkinter.set_appearance_mode('dark')
    customtkinter.set_default_color_theme("blue")
    window.title('Facial Feature Augmentation using GAN')
    window.after(0, lambda: window.wm_state('zoomed'))
    window.minsize(450, 550)
    # Create frame
    frame = customtkinter.CTkFrame(master=window)
    frame.pack(pady=10, padx=0, expand=TRUE, fill='none')
    # Create layout
    main(window, frame)
    # Run forever
    window.mainloop()
