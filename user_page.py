import os.path
import glob
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from imutils.object_detection import non_max_suppression
import database_page as cd
import login_page as lp
import shutil
import Augmentation_Project as ap
import customtkinter
from camera_webcam import camera_status
import about_page as about
from camera_webcam import get_filename, has_a_image, start_webcam, set_has_image
from PIL import Image
filename = ""
label, vid = '', ''


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
    print(filename, 'set file')


def browse_files(text):
    global filename
    if has_a_image() is False:
        filename = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=[("JPG", "*.jpg "),
                                                                                                ("JPEG", "*.jpeg")])
        text.config(state='normal')
        text.insert(INSERT, filename)
        text.config(state='disabled')
    else:
        filename = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=[("JPG", "*.jpg "),
                                                                                                ("JPEG", "*.jpeg")])
        start_webcam()
        text.config(state='normal')
        text.insert(INSERT, filename)
        text.config(state='disabled')


def create_caricature(frame, aug_frame, checked, text_box):
    global filename
    print(filename, "create caricture")
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
        folder = os.path.abspath("./Augmentation_Project/original_images")
        shutil.copy(fname, folder)
        folder = os.path.abspath("./Augmentation_Project/Snapshots")
        print(folder)
        shutil.copy(fname, folder)
        text_box.config(state='normal')
        text_box.delete("1.0", "end")
        text_box.config(state='disabled')
        filename = ''
        # call facial landmarking to update processed photo folder
        ap.Facial_Landmarking.main()
        ap.Augmenting_Features.main()
        error_label = customtkinter.CTkLabel(frame, text="Successfully Created Caricature!", text_color="green", font=('Times New Roman', 20))
        error_label.grid(row=4, column=0, columnspan=2)
        frame.after(3500, error_label.destroy)
        show_images_frame(aug_frame, frame, ('Times New Roman', 20), fname)
        aug_frame.tkraise()


def check_snapshot(filename, file_text):
    if (filename == '') and (file_text.get(1.0, "end-1c") == '') and (has_a_image()):
        filename = get_filename()
        print('snapshot', filename)
        return filename
    else:
        return filename


def webcam_view(frame1, file_text):
    frame1.after(1, camera_status(frame1, True, file_text))


def show_images_frame(frame, main_frame, font, file):
    # Make a label for the window
    frame1 = customtkinter.CTkFrame(master=frame, width=600, height=400)
    frame1.grid(row=0, column=0, columnspan=2)
    customtkinter.CTkLabel(frame1, text="Welcome to Facial Feature Augmentation", font=font).grid(row=0,
                                                                                                  column=0,
                                                                                                  columnspan=2,
                                                                                                  pady=50)
    if not(file == ''):
        orig_image = customtkinter.CTkImage(light_image=Image.open(file), dark_image=Image.open(file), size=(550, 450))
        customtkinter.CTkLabel(frame1, text="", image=orig_image).grid(row=1, column=0, padx=5, pady=60)
        newfile = f"Augmentation_Project/augmented_images/augmented_{os.path.basename(file)}"
        aug_image = customtkinter.CTkImage(light_image=Image.open(newfile), dark_image=Image.open(newfile), size=(550, 450))
        customtkinter.CTkLabel(frame1, text="", image=aug_image).grid(row=1, column=1, padx=5, pady=50)

    # Liability button
    customtkinter.CTkButton(frame1, text='Return to main Page', font=font, command=lambda: main_frame.tkraise()).grid(row=2, column=0, columnspan=2, pady=0)


def show_main_page_frame(frame, img_frame, font):
    # Make a label for the window
    frame1 = customtkinter.CTkFrame(master=frame, width=600, height=400)
    frame1.grid(row=0, column=0, columnspan=2, pady=20)
    customtkinter.CTkLabel(frame1, text="Welcome to Facial Feature Augmentation", font=font).grid(row=0, column=1)

    # Show the created Box
    frame2 = customtkinter.CTkFrame(master=frame, width=600)
    frame2.grid(row=1, column=0, columnspan=2, padx=80)
    button = customtkinter.CTkButton(frame2, text='Upload Image', font=font, command=lambda: browse_files(file_text))
    button.pack(pady=12, padx=10, side=LEFT)
    file_text = Text(frame2, height=1, width=100, state='disabled')
    file_text.pack(pady=12, padx=10, side=LEFT)
    # Make a button for browsing images the window
    webcam_view(frame1, file_text)
    # Liability button
    frame3 = customtkinter.CTkFrame(master=frame, width=600)
    frame3.grid(row=2, column=0, columnspan=2, pady=20, padx=10)
    checkbutton_var = BooleanVar()
    customtkinter.CTkCheckBox(frame3, text='I consent to having the photo and caricature added to a database for facial recognition research purposes only.',
                              variable=checkbutton_var, font=('Times New Roman', 15)).pack(pady=12, padx=10, side=BOTTOM)
    # Caricature button
    button = customtkinter.CTkButton(frame, text='Create Caricature', font=font, command=lambda: create_caricature(frame, img_frame, checkbutton_var.get(), file_text))
    button.grid(row=3, column=0, columnspan=2)
    string_var = StringVar()
    error_label = customtkinter.CTkLabel(frame, textvariable=string_var, font=('Times New Roman', 20))
    error_label.grid(row=4, column=1, columnspan=2)


# Create user window
def main(window, frame):
    font = ('Times New Roman', 20)
    mb = Menu(window)
    mb_dropdown = Menu(mb, tearoff=0)
    mb_dropdown.add_command(label="Logout", command=lambda: open_login(window, frame))
    mb_dropdown.add_command(label="About", command=lambda: open_about(window, frame))
    mb_dropdown.add_command(label="Database", command=lambda: open_database(window, frame))
    mb.add_cascade(label="Menu", menu=mb_dropdown)
    window.config(menu=mb)
    main_frame = customtkinter.CTkFrame(frame, width=600, height=800)
    image_frame = customtkinter.CTkFrame(frame)
    show_main_page_frame(main_frame, image_frame, font)
    main_frame.grid(row=0, column=0)
    image_frame.grid(row=0, column=0)
    main_frame.tkraise()
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
    frame = customtkinter.CTkFrame(master=window, width=300)
    frame.pack(pady=10, padx=0, expand=TRUE, fill='none')
    # Create layout
    main(window, frame)
    # Run forever
    window.mainloop()
