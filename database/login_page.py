# login_page.py

<<<<<<< HEAD
<<<<<<< HEAD
import sys
import os
from tkinter import *
import database.user_page as up
import createuser_page as cu
import database.forgotpassword_page as fp
import bcrypt
import sqlite3
import customtkinter
from PIL import Image
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)

=======
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
from tkinter import Tk, Label, Entry, Button
import bcrypt
import sqlite3
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
import database.createuser_page as cu
import database.user_page as up
import database.forgotpassword_page as fp
<<<<<<< HEAD
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96

# Make database if not exist
def make_user_database():
    connection = sqlite3.connect('user_data.db')
    user = connection.cursor()
    user.execute('''CREATE TABLE IF NOT EXISTS 'users' (id text, email text, password text, unique(email))''')
    connection.commit()


# Function to verify user credentials
def verify_credentials(email, password):
    # gets hashed password from database
    conn = sqlite3.connect('user_data.db')
    verify_cred = conn.cursor()
    verify_cred.execute("""SELECT password From users Where email=?""", (email,))
    hashed_password = verify_cred.fetchone()
    # if there is a hashed password compare with input password
    if hashed_password:
        # return if input password matches hashed password
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password[0])
    else:
        return False


<<<<<<< HEAD
<<<<<<< HEAD
def clear_frame(frame):
    for widgets in frame.winfo_children():
        widgets.destroy()


# Open user window
def open_user_window(win, email, password, frame):
    if verify_credentials(email, password):
        clear_frame(frame)
        up.main(win, frame)
    else:
        error_message_box(frame, "Invalid credentials!", 'red')


# Open create user page
def open_create_user_window(wind, frame):
    clear_frame(frame)
    cu.create_user(wind, frame)


# Open forgot password window
def open_forgot_password_window(wind, frame):
    clear_frame(frame)
    fp.forgot_user(wind, frame)


# Show error message in window
def error_message_box(frame, message, color):
    error_label = customtkinter.CTkLabel(frame, text=message, text_color=color, font=('Times New Roman', 20))
    error_label.pack(pady=12, padx=10, anchor='c', side=BOTTOM)
    frame.after(3500, error_label.destroy)


def create_main_page(window, frame):
    # Make a label for the window
    font = ('Times New Roman', 20)
    my_image = customtkinter.CTkImage(light_image=Image.open('icons/comic_contours_icon.png'),
                                      dark_image=Image.open('icons/comic_contours_icon.png'), size=(450, 150))
    customtkinter.CTkLabel(frame, text="", image=my_image).pack(pady=20)
    customtkinter.CTkLabel(frame, text="Login", font=('Times New Roman', 40)).pack(pady=20)
    email_entry = customtkinter.CTkEntry(frame, placeholder_text="Email", font=font, width=200)
    email_entry.pack(pady=12, padx=10, side=TOP)
    password_entry = customtkinter.CTkEntry(frame, show="*", placeholder_text="Password", font=font, width=200)
    password_entry.pack(pady=12, padx=10, side=TOP)
    login_button = customtkinter.CTkButton(frame, text='Login', font=font, command=lambda: open_user_window(window, email_entry.get(), password_entry.get(), frame))
    login_button.pack(pady=12, padx=10, side=TOP)
    create_account_button = customtkinter.CTkButton(frame, text='Create Account', font=font, command=lambda: open_create_user_window(window, frame))
    create_account_button.pack(pady=12, padx=10, anchor='w', side=BOTTOM)
    label = customtkinter.CTkLabel(frame, text="Forgot Password?", font=font)
    label.bind("<Button-1>", lambda e: open_forgot_password_window(window, frame))
    label.pack(pady=12, padx=10, anchor='w', side=BOTTOM)
=======
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
# Open user window
def open_user_window(win, email, password):
    if verify_credentials(email, password):
        win.destroy()
        up.main()
    else:
        error_message_box(win, "Invalid credentials!")


# Open create user page
def open_create_user_window(wind):
    wind.destroy()
    cu.create_user()


# Open forgot password window
def open_forgot_password_window(win):
    win.destroy()
    fp.forgot_user()


# Show error message in window
def error_message_box(win, message):
    error_label = Label(win, text=message, fg="red")
    error_label.grid(row=6, column=2)
    win.after(3500, error_label.destroy)
<<<<<<< HEAD
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96


# Create login window
def main():
    # database
    make_user_database()
<<<<<<< HEAD
<<<<<<< HEAD

    # create main window
    window = customtkinter.CTk()
    customtkinter.set_appearance_mode('dark')
    customtkinter.set_default_color_theme("blue")
    window.title('Facial Feature Augmentation using GAN')
    window.after(0, lambda: window.wm_state('zoomed'))
    window.minsize(450, 600)
    # Create label user info
    frame = customtkinter.CTkFrame(master=window, width=300)
    frame.pack(pady=10, padx=0, expand=TRUE, fill='none')
    create_main_page(window, frame)
=======
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
    # create main window
    window = Tk()
    window.title('Facial Feature Augmentation using GAN')
    window.geometry("475x160")
    # Make a label for the window
    Label(window, text="Login").grid(row=0, column=0)
    # Create label user info
    Label(window, text="Email").grid(row=1, column=1)
    Label(window, text="Password").grid(row=2, column=1)
    email_entry = Entry(window)
    email_entry.grid(row=1, column=2)
    password_entry = Entry(window, show="*")
    password_entry.grid(row=2, column=2)
    label = Label(window, text="Forgot Password?", font=('Times New Roman', 8))
    label.bind("<Button-1>", lambda e: open_forgot_password_window(window))
    label.grid(row=3, column=1)
    # Create login button, when pressed call open user window function
    login_button = Button(window, text='Login', width=25, command=lambda: open_user_window(window, email_entry.get(), password_entry.get()))
    login_button.grid(row=4, column=2)
    create_account_button = Button(window, text='Create Account', width=15, command=lambda: open_create_user_window(window))
    create_account_button.grid(row=5, column=1)
<<<<<<< HEAD
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
=======
>>>>>>> ea733d2c58fe005ecb33c010077b68f1589e4d96
    # Run forever
    window.mainloop()


if __name__ == "__main__":
    main()
