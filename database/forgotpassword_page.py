# forgotpassword_page.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
from tkinter import *
import smtplib
import sqlite3
import bcrypt
from email.message import EmailMessage
import secrets
import customtkinter
from PIL import Image
import re
import database.login_page as lp

# Function to find user by email
def find_user_email(email):
    connection = sqlite3.connect('user_data.db')
    find_user = connection.cursor()
    find_user.execute("""SELECT id From users Where email=?""", (email,))
    user_name = find_user.fetchone()[0]
    return user_name

# Function to send email SMTP
def send_reset_email(frame, user_email):
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
        lp.error_message_box(frame, "Error: No Email Found, Please Create User", "red")
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

# Function to validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

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
