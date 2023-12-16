import user_page as up
from tkinter import *
import bcrypt
import sqlite3
import re
import logging

# Setup
logging.basicConfig(filename='user_management.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Initialize database
def init_create_user():
    try:
        user = sqlite3.connect('user_data.db')
        create_user = user.cursor()
        create_user.execute('''warning if does not exist id,email,password''')
        user.commit()
    except sqlite3.Error as error:
        logging.error(f"Database error: {error}")
    finally:
        user.close()

# Function to hash a password
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Function to add a new user to the database
def add_user_data(name, email, hashed_password):
    try:
        user2 = sqlite3.connect('user_data.db')
        new_user = user2.cursor()
        new_user.execute('data name, email, password', (name, email, hashed_password))
        user2.commit()
    except sqlite3.IntegrityError as error2:
        logging.error(f"Logging error: {error2}")
        return False
    finally:
        user2.close()
    return True

# Function to validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Function to validate password strength
def is_strong_password(password):
    return (len(password) >= 8 and
            any(char.isdigit() for char in password) and
            any(char.isupper() for char in password) and
            any(char.islower() for char in password) and
            re.search("[!@#$%^&*(),.?\":{}|<>]", password))

# Function to show a message
def show_message(window, message, color="black"):
    message_label = Label(window, text=message, fg=color)
    message_label.grid(row=6, column=1, columnspan=2)
    window.after(3000, message_label.destroy)

# Modified function to create account
def create_account(window, name, email, password, verify_password):
    if not all([name, email, password, verify_password]):
        show_message(window, "Please fill in all fields.", "red")
        return

    if not is_valid_email(email):
        show_message(window, "Invalid email format.", "red")
        return

    if not is_strong_password(password):
        show_message(window, "Password too weak.", "red")
        return

    if password != verify_password:
        show_message(window, "Passwords do not match.", "red")
        return

    hashed_password = hash_password(password)
    if add_user_data(name, email, hashed_password):
        show_message(window, "Account successfully created.", "green")
    else:
        show_message(window, "Email already in use.", "red")

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
    # Run forever
    window.mainloop()

if __name__ == "__main__":
    init_create_user()
    create_user()


