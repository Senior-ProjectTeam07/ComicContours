import numpy as np
import cv2
from PIL import ImageTk
import PIL.Image
from tkinter import *
from tkinter import filedialog
import cloudstorage
import customtkinter
from instapy_cli import client
from google.appengine.api import app_identity
import datetime
from google.cloud import storage
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
import database.user_page as up
import database.login_page as lp
import database.about_page as ap
original_list, processed_list, augmented_list, current_img, current_num = [], [], [], '', 0
small_original_list, small_processed_list, small_augmented_list = [], [], []
window = ''
from google.appengine.ext import testbed
from google.appengine.ext import db
from google.cloud import datastore

def open_user_window(wind, frame):
    lp.clear_frame(frame)
    up.main(wind, frame)

def open_login_window(wind, frame):
    lp.clear_frame(frame)
    lp.create_main_page(wind, frame)

def open_about(wind, frame):
    lp.clear_frame(frame)
    ap.main(wind, frame)

def browse_files():
    global current_img
    img = ImageTk.getimage(current_img)
    folder_path = filedialog.askdirectory(initialdir="/", title="Select a Folder")
    print(folder_path)
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    cv2.imwrite(f'{folder_path}/new_img.jpeg', img)

def get_frame_img(frame, img_no):
    global current_img, current_num
    label = ''
    current_num = img_no
    # for getting image that is displayed, resetting buttons
    if frame == orig_frame:
        label = Label(frame, image=original_list[img_no])
        current_img = original_list[img_no]
    if frame == process_frame:
        label = Label(frame, image=processed_list[img_no])
        current_img = processed_list[img_no]
    if frame == augmented_frame:
        label = Label(frame, image=augmented_list[img_no])
        current_img = augmented_list[img_no]
    return label

def delete_image_of_person():
    global original_list, processed_list, augmented_list, current_num
    np.delete(original_list, current_num, 0)
    np.delete(processed_list, current_num, 0)
    np.delete(augmented_list, current_num, 0)
    folder = os.listdir('../data/original_images')
    img_name = folder[current_num]
    os.remove(f'../data/original_images/{img_name}')
    os.remove(f'../data/processed_images/Processed_{img_name}')
    os.remove(f'../data/augmented_images/augmented_{img_name}')
    if 'snapshot_' in img_name:
        os.remove(f'../data/Snapshots/{img_name}')
        os.remove(f'../database/Webcam_Snapshots/{img_name}')

def get_photo_folder(type_photo):
    global small_original_list, small_processed_list, small_augmented_list
    dir_path = ''
    if type_photo == "Original Photos":
        dir_path = '../data/original_images'
    if type_photo == "Processed Photos":
        dir_path = '../data/processed_images'
    if type_photo == "Augmented Photos":
        dir_path = '../data/augmented_images'
    folder = os.listdir(dir_path)
    image_list = []
    num_images = 0
    for num_images, file in enumerate(folder):
        img_path = os.path.join(dir_path, file)
        image = PIL.Image.open(img_path)
        resized_img = image.resize((700, 600))
        img = ImageTk.PhotoImage(resized_img)
        image_list.append(img)
        if type_photo == "Original Photos":
            resized_img = image.resize((100, 50))
            img = ImageTk.PhotoImage(resized_img)
            small_original_list.append(img)
        if type_photo == "Processed Photos":
            resized_img = image.resize((100, 50))
            img = ImageTk.PhotoImage(resized_img)
            small_processed_list.append(img)
        if type_photo == "Augmented Photos":
            resized_img = image.resize((100, 50))
            img = ImageTk.PhotoImage(resized_img)
            small_augmented_list.append(img)
    return num_images, image_list

def back(img_no, label, tot_img, btn_fwd, btn_back, frame):
    global original_list, processed_list, augmented_list
    label.grid_forget()
    btn_fwd.grid_forget()
    btn_back.grid_forget()
    label = get_frame_img(frame, img_no)
    btn_fwd = customtkinter.CTkButton(frame, text="Forward", command=lambda: forward(img_no+1, label, tot_img, btn_fwd, btn_back, frame))
    btn_back = customtkinter.CTkButton(frame, text="Back", command=lambda: back(img_no-1, label, tot_img, btn_fwd, btn_back, frame))

    # whenever the first image, have the back button disabled
    if img_no == 0:
        btn_back = customtkinter.CTkButton(frame, text="Back", state=DISABLED)
    label.grid(row=1, column=0, columnspan=3, padx=20)
    btn_back.grid(row=5, column=0)
    btn_fwd.grid(row=5, column=2)

def forward(img_no, label, tot_img, btn_fwd, btn_back, frame):
    global original_list, processed_list, augmented_list
    label.grid_forget()
    btn_fwd.grid_forget()
    btn_back.grid_forget()

    label = get_frame_img(frame, img_no)
    # img_no+1 as we want the next image to pop up when clik forward
    btn_fwd = customtkinter.CTkButton(frame, text="Forward", command=lambda: forward(img_no+1, label, tot_img, btn_fwd, btn_back, frame))
    # disable button for first and last photo
    if img_no == tot_img:
        btn_fwd = customtkinter.CTkButton(frame, text="Forward", state=DISABLED)
    if img_no == 0:
        btn_back = customtkinter.CTkButton(frame, text="Back", state=DISABLED)
    # img_no-1 as we want previous image when click back
    btn_back = customtkinter.CTkButton(frame, text="Back", command=lambda: back(img_no-1, label, tot_img, btn_fwd, btn_back, frame))
    # Placing the button in new grid
    label.grid(row=1, column=0, columnspan=3, padx=20)
    btn_back.grid(row=5, column=0)
    btn_fwd.grid(row=5, column=2)

def jump_to_photo(img_no, label, btn_fwd, btn_back, tot_img, frame):
    global original_list, processed_list, augmented_list
    label.grid_forget()
    btn_fwd.grid_forget()
    btn_back.grid_forget()

    label = get_frame_img(frame, img_no)
    if img_no == tot_img:
        btn_fwd = customtkinter.CTkButton(frame, text="Forward", state=DISABLED)
    else:
        btn_fwd = customtkinter.CTkButton(frame, text="Forward", command=lambda: forward(img_no+1, label, tot_img, btn_fwd, btn_back, frame))
    if img_no == 0:
        btn_back = customtkinter.CTkButton(frame, text="Back", state=DISABLED)
    else:
        btn_back = customtkinter.CTkButton(frame, text="Back", command=lambda: back(img_no-1, label, tot_img, btn_fwd, btn_back, frame))
    # Placing the button in new grid
    label.grid(row=1, column=0, columnspan=3, padx=20)
    btn_back.grid(row=5, column=0)
    btn_fwd.grid(row=5, column=2)
def upload_to_insta(username, password, caption):
    global current_img
    img = ImageTk.getimage(current_img)
    username = username
    password = password
    image = img
    text = caption
    with client(username, password) as cli:
        cli.upload(image, text)
def insta_popup():
    global window
    top = Toplevel(window)
    top.title("Insta Window")
    # top.geometry('400x200')
    customtkinter.CTkLabel(top, text="Please Enter Instagram Information to Upload", text_color='black').pack()
    user_entry = customtkinter.CTkEntry(top, placeholder_text="Username", font=('Times New Roman', 20), width=200)
    user_entry.pack()
    password_entry = customtkinter.CTkEntry(top, show="*", placeholder_text="Password", font=('Times New Roman', 20), width=200)
    password_entry.pack()
    caption_entry = customtkinter.CTkEntry(top, placeholder_text="Caption", font=('Times New Roman', 20), width=200)
    caption_entry.pack()
    login_button = customtkinter.CTkButton(top, text='Login', font=('Times New Roman', 20), command=lambda: upload_to_insta(user_entry.get(), password_entry.get(), caption_entry.get()))
    login_button.pack()

def upload_cloud_file(frame):
    global current_img, current_num
    image = current_img
    folder = os.listdir('../data/original_images')
    filename = folder[current_num]
    bucket_name = '<bucket_name>'
    # Explicitly use service account credentials by specifying the private key
    # file.
    try:
        storage_client = storage.Client.from_service_account_json('creds.json')
        # or storage_client = storage.Client.from_service_account_json('key.json')
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob('chosen-path-to-object/{name-of-object}')
        blob.upload_from_filename(filename)
        error_label = customtkinter.CTkLabel(frame, text="Successful", text_color='green')
        error_label.grid(row=1, column=0, columnspan=2)
        frame.after(3500, error_label.destroy)
        return blob.public_url
    except:
        error_label = customtkinter.CTkLabel(frame, text="Please install google cloud platform", text_color='red')
        error_label.grid(row=1, column=0, columnspan=2)
        frame.after(3500, error_label.destroy)

def make_frame_btns(frame):
    # makes buttons that switch to other frames
    orig_butt = customtkinter.CTkButton(frame, text="Original Photos", command=lambda: orig_frame.tkraise())
    process_butt = customtkinter.CTkButton(frame, text="Processed Photos", command=lambda: process_frame.tkraise())
    aug_butt = customtkinter.CTkButton(frame, text="Augmented Photos", command=lambda: augmented_frame.tkraise())
    # disables button for current frame
    if frame == orig_frame:
        orig_butt = customtkinter.CTkButton(frame, text="Original Photos", state=DISABLED)
    if frame == process_frame:
        process_butt = customtkinter.CTkButton(frame, text="Processed Photos", state=DISABLED)
    if frame == augmented_frame:
        aug_butt = customtkinter.CTkButton(frame, text="Augmented Photos", state=DISABLED)
    # puts buttons on grid
    orig_butt.grid(row=0, column=0, sticky="n")
    process_butt.grid(row=0, column=1, sticky="n")
    aug_butt.grid(row=0, column=2, sticky="n")

def make_frame(frame):
    global original_list, processed_list, augmented_list, current_img, current_num
    # make original photo, processed photo, and augmented photo buttons
    make_frame_btns(frame)
    # put images in list, display first image
    num_img = 0
    if frame == orig_frame:
        num_img, original_list = get_photo_folder("Original Photos")
    if frame == process_frame:
        num_img, processed_list = get_photo_folder("Processed Photos")
    if frame == augmented_frame:
        num_img, augmented_list = get_photo_folder("Augmented Photos")
    label = get_frame_img(frame, 0)
    current_num = 0
    label.grid(row=1, column=0, columnspan=3, padx=20)
    # We will have button back, and forward
    frame_btns = customtkinter.CTkFrame(frame, bg_color='black')
    button_back = customtkinter.CTkButton(frame, text="Back", command=back, state=DISABLED)
    button_forward = customtkinter.CTkButton(frame, text="Forward", command=lambda: forward(1, label, num_img,
                                                                                            button_forward, button_back,
                                                                                            frame))
    # Create a frame for the canvas
    frame_canvas = customtkinter.CTkFrame(frame_btns, bg_color='black')

    # canvas
    canvas = customtkinter.CTkCanvas(frame_canvas, bg='black', background='black')
    canvas.grid(row=0, column=0, sticky="ns")
    # make scrollbar for image numbers on canvas
    scrollbar = customtkinter.CTkScrollbar(frame_canvas, orientation="vertical", command=canvas.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    canvas.configure(yscrollcommand=scrollbar.set)
    btn_frame = customtkinter.CTkFrame(canvas)
    canvas.create_window((0, 0), window=btn_frame, anchor='nw')
    # make button number for num images and allow button to jump to photo
    button = list(range(0, num_img+1))
    img = ''
    for i in range(0, num_img+1):
        if frame == orig_frame:
            img = small_original_list[i]
        if frame == process_frame:
            img = small_processed_list[i]
        if frame == augmented_frame:
            img = small_augmented_list[i]
        button[i] = Button(btn_frame, text='', image=img, command=lambda i=i: jump_to_photo(i, label, button_forward, button_back, num_img, frame))
        button[i].grid(row=i, column=0, sticky="news")
    btn_frame.update_idletasks()
    btn_width = (button[0].winfo_width())
    # set scroll bar to only display 14 num buttons, otherwise need to scroll
    if num_img <= 14:
        btn_height = sum(button[i].winfo_height() for i in range(0, num_img+1))
    else:
        btn_height = sum(button[i].winfo_height() for i in range(0, 15))
    canvas.configure(width=btn_width)
    frame_canvas.configure(width=btn_width, height=btn_height)
    canvas.configure(scrollregion=canvas.bbox("all"))
    button_download = customtkinter.CTkButton(frame_btns, text="Download image", fg_color='dark blue', command=lambda: browse_files())
    button_delete = customtkinter.CTkButton(frame_btns, text="Delete image", fg_color='dark blue', command=lambda: delete_image_of_person())
    insta_img = customtkinter.CTkImage(PIL.Image.open("./icons/Instagram_icon.png"), size=(30, 30))
    icloud_img = customtkinter.CTkImage(PIL.Image.open("./icons/google_cloud.png"), size=(30, 30))
    social_frame = customtkinter.CTkFrame(frame_btns, bg_color='black')
    button_insta = customtkinter.CTkButton(social_frame, text="", fg_color='dark blue', image=insta_img, width=30, command=lambda: insta_popup())
    button_cloud = customtkinter.CTkButton(social_frame, text="", fg_color='dark blue', image=icloud_img, width=30, command=lambda: upload_cloud_file(social_frame))
    frame_btns.grid(row=0, column=6, rowspan=3, sticky='nw', pady=20)
    customtkinter.CTkLabel(frame_btns, text="Jump to photo", text_color='grey').pack()
    frame_canvas.pack()
    button_download.pack(pady=15)
    button_delete.pack()
    social_frame.pack(pady=10)
    button_insta.grid(row=0, column=0)
    button_cloud.grid(row=0, column=1)
    button_back.grid(row=5, column=0)
    button_forward.grid(row=5, column=2)

# Main
def main(wind, frame):
    global orig_frame, process_frame, augmented_frame, window
    # create window
    window = wind
    mb = Menu(window)
    mb_dropdown = Menu(mb, tearoff=0)
    mb_dropdown.add_command(label="Logout", font=('Times New Roman', 20), command=lambda: open_login_window(window, frame))
    mb_dropdown.add_command(label="About", font=('Times New Roman', 20), command=lambda: open_about(window, frame))
    mb_dropdown.add_command(label="Main Page", font=('Times New Roman', 20), command=lambda: open_user_window(window, frame))
    mb.add_cascade(label="Menu", menu=mb_dropdown)
    window.config(menu=mb)
    orig_frame = customtkinter.CTkFrame(frame)
    process_frame = customtkinter.CTkFrame(frame)
    augmented_frame = customtkinter.CTkFrame(frame)
    make_frame(orig_frame)
    make_frame(process_frame)
    make_frame(augmented_frame)
    orig_frame.grid(row=0, column=0)
    process_frame.grid(row=0, column=0)
    augmented_frame.grid(row=0, column=0)
    orig_frame.tkraise()
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
    frame = customtkinter.CTkFrame(master=window, width=300)
    frame.pack(pady=10, padx=0, expand=TRUE, fill='none')
    # Create layout
    main(window, frame)
