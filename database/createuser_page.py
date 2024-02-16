import database.user_page as up
import database.login_page as lp
from tkinter import *
import bcrypt
import sqlite3
import re


# Database
def make_user_database():
    connection = sqlite3.connect('user_data.db')
    user = connection.cursor()
    user.execute('''CREATE TABLE IF NOT EXISTS 'users' (id text, email text, password text, unique(email)''')
    connection.commit()


# Function to hash a password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


# Function to add a new user to the database
def add_user_data(window, name, email, hashed_password):
    conn = sqlite3.connect('user_data.db')
    new_user = conn.cursor()
    try:
        new_user.execute("INSERT Into users VALUES(?,?,?)", [name, email, hashed_password])
    except sqlite3.Error:
        show_message(window, "Error: Email already in use", "red")

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
        return False, "Password must contain a lowercase letter"
    if not(any(char.islower() for char in password)):
        return False, "Password must contain an uppercase letter"
    if not(any(char in special_char for char in password)):
        return False, "Password must contain a special character"
    return True, ""


# Function to show a message
def show_message(window, message, color):
    message_label = Label(window, text=message, fg=color)
    message_label.grid(row=6, column=1, columnspan=2)
    window.after(3000, message_label.destroy)


def open_user_page(window):
    window.destroy()
    up.main()


# Modified function to create account
def create_account(win, name, email, password, verify_password):
    is_strong, message = is_password_strong(password)
    hashed_password = hash_password(password)
    if not all([name, email, password, verify_password]):
        show_message(win, "Please fill in all fields.", "red")
    elif not is_valid_email(email):
        show_message(win, "Invalid email format.", "red")
    elif is_strong is False:
        show_message(win, message, "red")
    elif password != verify_password:
        show_message(win, "Passwords do not match.", "red")
    elif add_user_data(win, name, email, hashed_password):
        show_message(win, "Account successfully created.", "green")
        win.destroy()
        up.main()
        return
    else:
        show_message(win, "Email already in use.", "red")


def open_login_window(win):
    win.destroy()
    lp.main()


# Function to create user
def create_user():
    # create main window
    window = Tk()
    window.title('Facial Feature Augmentation using GAN')
    window.geometry("400x200")
    # Make a label for the window
    Label(window, text="Create User").grid(row=0)
    # Create label user info
    Label(window, text="Name").grid(row=1, column=1)
    Label(window, text="Email").grid(row=2, column=1)
    Label(window, text="Password").grid(row=3, column=1)
    Label(window, text="Verify Password").grid(row=4, column=1)
    name_entry = Entry(window)
    name_entry.grid(row=1, column=2)
    email_entry = Entry(window)
    email_entry.grid(row=2, column=2)
    password_entry = Entry(window, show="*")
    password_entry.grid(row=3, column=2)
    verify_password_entry = Entry(window, show="*")
    verify_password_entry.grid(row=4, column=2)
    # Create login button, when pressed call open user window function
    create_button = Button(window, text='Create Account', width=15, command=lambda: create_account(window, name_entry.get(), email_entry.get(), password_entry.get(), verify_password_entry.get()))
    create_button.grid(row=5, column=2)
    label = Label(window, text="Return to login page", font=('Times New Roman', 8))
    label.bind("<Button-1>", lambda e: open_login_window(window))
    label.grid(row=6, column=2)
    # Run forever
    window.mainloop()


if __name__ == "__main__":
    make_user_database()
    create_user()
