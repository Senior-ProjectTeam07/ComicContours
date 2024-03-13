import user_page as up
import login_page as lp
from tkinter import *
import bcrypt
import sqlite3
import re
import customtkinter
from PIL import Image


# Function to hash a password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


# Function to add a new user to the database
def add_user_data(frame, name, email, hashed_password):
    conn = sqlite3.connect('user_data.db')
    new_user = conn.cursor()
    try:
        new_user.execute("INSERT Into users VALUES(?,?,?)", [name, email, hashed_password])
    except sqlite3.Error:
        lp.error_message_box(frame, "Error: Email already in use", "red")

    conn.commit()
    conn.close()
    return True


# Function to validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


# Function to validate password strength
def is_password_strong(password):
    # Set special characters that are acceptable
    special_char = "!@#$%^&*()_+-=<>?"
    # checks to see if length greater or equal to 8
    # any character in password is digit, uppercase, lowercase, and special character
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not(any(char.isdigit() for char in password)):
        return False, "Password must contain a digit"
    if not(any(char.isupper() for char in password)):
        return False, "Password must contain a uppercase letter"
    if not(any(char.islower() for char in password)):
        return False, "Password must contain an lowercase letter"
    if not(any(char in special_char for char in password)):
        return False, "Password must contain a special character"
    return True, ""


# Modified function to create account
def create_account(win, frame, name, email, password, verify_password):
    is_strong, message = is_password_strong(password)
    hashed_password = hash_password(password)
    if not all([name, email, password, verify_password]):
        lp.error_message_box(frame, "Please fill in all fields.", "red")
    elif not is_valid_email(email):
        lp.error_message_box(frame, "Invalid email format.", "red")
    elif is_strong is False:
        lp.error_message_box(frame, message, "red")
    elif password != verify_password:
        lp.error_message_box(frame, "Passwords do not match.", "red")
    elif add_user_data(frame, name, email, hashed_password):
        lp.error_message_box(frame, "Account successfully created.", "green")
        lp.clear_frame(frame)
        up.main(win, frame)
        return
    else:
        lp.error_message_box(frame, "Email already in use.", "red")


def open_login_window(window, frame):
    lp.clear_frame(frame)
    lp.create_main_page(window, frame)


# Function to create user
def create_user(window, frame):
    # Make a label for the window
    font = ('Times New Roman', 20)
    my_image = customtkinter.CTkImage(light_image=Image.open('icons/comic_contours_icon.png'),
                                      dark_image=Image.open('icons/comic_contours_icon.png'), size=(450, 150))
    customtkinter.CTkLabel(frame, text="", image=my_image).pack(pady=20)
    customtkinter.CTkLabel(frame, text="Create User", font=('Times New Roman', 40)).pack(pady=12, padx=10, side=TOP)

    # Create Entries for user info
    name_entry = customtkinter.CTkEntry(frame, placeholder_text="Name", font=font, width=200)
    name_entry.pack(pady=12, padx=10, side=TOP)
    email_entry = customtkinter.CTkEntry(frame, placeholder_text="Email", font=font, width=200)
    email_entry.pack(pady=12, padx=10, side=TOP)
    password_entry = customtkinter.CTkEntry(frame, show="*", placeholder_text="Password", font=font, width=200)
    password_entry.pack(pady=12, padx=10, side=TOP)
    verify_password_entry = customtkinter.CTkEntry(frame, show="*", placeholder_text="Verify Password", font=font, width=200)
    verify_password_entry.pack(pady=12, padx=10, side=TOP)

    # Create account button, when pressed call open user window function
    create_button = customtkinter.CTkButton(frame, text='Create Account', font=font,
                                            command=lambda: create_account(window, frame, name_entry.get(),
                                                                           email_entry.get(), password_entry.get(),
                                                                           verify_password_entry.get()))
    create_button.pack(pady=12, padx=10, side=TOP)
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
    create_user(window, frame)
    # Run forever
    window.mainloop()
