# login_page.py

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


# Create login window
def main():
    # database
    make_user_database()
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
    # Run forever
    window.mainloop()


if __name__ == "__main__":
    main()
