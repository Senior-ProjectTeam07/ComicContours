# forgotpassword_page.py

<<<<<<< HEAD
<<<<<<< HEAD
from tkinter import *
=======
from tkinter import Tk, Label, Entry, Button
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
=======
from tkinter import Tk, Label, Entry, Button
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
import smtplib
import sqlite3
import bcrypt
from email.message import EmailMessage
import secrets
<<<<<<< HEAD
import customtkinter
from PIL import Image
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
import re
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
import database.login_page as lp

<<<<<<< HEAD
<<<<<<< HEAD
=======
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
# Make database if not exist
def make_user_database():
    connection = sqlite3.connect('user_data.db')
    user = connection.cursor()
    user.execute('''CREATE TABLE IF NOT EXISTS 'users' (id text, email text, password text, unique(email))''')
    connection.commit()


>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
# Function to find user by email
def find_user_email(email):
    connection = sqlite3.connect('user_data.db')
    find_user = connection.cursor()
    find_user.execute("""SELECT id From users Where email=?""", (email,))
    user_name = find_user.fetchone()[0]
    return user_name

<<<<<<< HEAD
# Function to send email SMTP
def send_reset_email(frame, user_email):
=======

# Function to send email SMTP
def send_reset_email(window, user_email):
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
    # make new random password
    password_length = 8
    password = secrets.token_urlsafe(password_length)
    # get Name and input new Password into database
    hash_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('user_data.db')
    new_password = conn.cursor()
    try:
        new_password.execute("Update users set password = ? where email = ? ", [hash_password, user_email])
    except sqlite3.Error:
<<<<<<< HEAD
        lp.error_message_box(frame, "Error: No Email Found, Please Create User", "red")
=======
        show_message(window, "Error: No Email Found, Please Create User", "red")
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
    conn.commit()
    conn.close()
    connection = sqlite3.connect('user_data.db')
    find_user = connection.cursor()
    find_user.execute("""SELECT id From users Where email=?""", (user_email,))
    user_name = find_user.fetchone()[0]
    connection.close()
    # make message
    email_sender = 'seniorproject.faceaugmentation@gmail.com'
    msg = EmailMessage()
    msg['Subject'] = 'Forgot Password'
    msg['From'] = email_sender
    msg['To'] = user_email
    content = 'Hello ' + user_name + ", your new generated password to Facial Feature Augmentation using GAN Software is '" + password + "'. If you are not using the software then please discard this message. Do not reply."
    msg.set_content(content)

    # send message to user
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as send_email:
        send_email.login(email_sender, 'ioyaakqmspzggilz')
        send_email.sendmail(email_sender, user_email, msg.as_string())

<<<<<<< HEAD
=======

>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
# Function to validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

<<<<<<< HEAD
# Function to handle the forgot password logic
def handle_forgot_password(frame, name, email):
    if not name or not email:
        lp.error_message_box(frame, "Please enter all details!", "red")
        return
    if not is_valid_email(email):
        lp.error_message_box(frame, "Invalid email format!", 'red')
        return
    user = find_user_email(email)
    if user and (user == name):
        send_reset_email(frame, email)
        lp.error_message_box(frame, "New password sent to email.", 'green')
    else:
        lp.error_message_box(frame, "User not found!", 'red')

def open_login_window(wind, frame):
    lp.clear_frame(frame)
    lp.create_main_page(wind, frame)

# Function to create the forgot password window
def forgot_user(window, frame):
    # Make a label for the window
    font = ('Times New Roman', 20)
    my_image = customtkinter.CTkImage(light_image=Image.open('icons/comic_contours_icon.png'),
                                      dark_image=Image.open('icons/comic_contours_icon.png'), size=(450, 150))
    customtkinter.CTkLabel(frame, text="", image=my_image).pack(pady=20)
    customtkinter.CTkLabel(frame, text="Forgot Password", font=('Times New Roman', 40)).pack(pady=12, padx=10, side=TOP)
    # Create label user info
    name_entry = customtkinter.CTkEntry(frame, placeholder_text="Name", font=font, width=200)
    name_entry.pack(pady=12, padx=10, side=TOP)
    email_entry = customtkinter.CTkEntry(frame, placeholder_text="Email", font=font, width=200)
    email_entry.pack(pady=12, padx=10, side=TOP)
    # Create send email button, when pressed sends password to email
    send_button = customtkinter.CTkButton(frame, text='Send Email', font=font,
                                          command=lambda: handle_forgot_password(frame, name_entry.get(), email_entry.get()))
    send_button.pack(pady=12, padx=10, side=TOP)
    label = customtkinter.CTkLabel(frame, text="Return to login page", font=font)
    label.bind("<Button-1>", lambda e: open_login_window(window, frame))
    label.pack(pady=12, padx=10, anchor='w', side=BOTTOM)

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
    forgot_user(window, frame)
    # Run forever
    window.mainloop()
=======

# Function to show a message to the user
def show_message(window, message, color='red'):
    message_label = Label(window, text=message, fg=color)
    message_label.grid(row=5, column=1, columnspan=2)
    window.after(3000, message_label.destroy)


# Function to handle the forgot password logic
def handle_forgot_password(window, name, email):
    if not name or not email:
        show_message(window, "Please enter all details.")
        return
    if not is_valid_email(email):
        show_message(window, "Invalid email format.")
        return

    user = find_user_email(email)
    if user and (user == name):
        send_reset_email(window, email)
        show_message(window, "New password sent to email.", color='green')
    else:
        show_message(window, "User not found.", color='red')


def open_login_window(win):
    win.destroy()
    lp.main()


# Function to create the forgot password window
def forgot_user():
    # create main window
    window = Tk()
    window.title('Facial Feature Augmentation using GAN')
    window.geometry("400x150")
    # Make a label for the window
    Label(window, text="Forgot Password").grid(row=0, column=1)
    # Create label user info
    Label(window, text="Name").grid(row=1, column=0)
    Label(window, text="Email").grid(row=2, column=0)
    name_entry = Entry(window)
    name_entry.grid(row=1, column=1)
    email_entry = Entry(window)
    email_entry.grid(row=2, column=1)
    # Create send email button, when pressed sends password to email
    send_button = Button(window, text='Send Email', width=15, command=lambda: handle_forgot_password(window, name_entry.get(), email_entry.get()))
    send_button.grid(row=3, column=1)
    label = Label(window, text="Return to login page", font=('Times New Roman', 8))
    label.bind("<Button-1>", lambda e: open_login_window(window))
    label.grid(row=4, column=1)
    # Run forever
    window.mainloop()


if __name__ == "__main__":
    make_user_database()
    forgot_user()
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
