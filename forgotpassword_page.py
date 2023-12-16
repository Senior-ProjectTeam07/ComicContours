from tkinter import *
import login_page as lp
import sqlite3
import smtplib
from email.mime.text import MIMEText
import re
import logging

# Setup
logging.basicConfig(filename='user_management.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Initialize the database
def init_user_data():
    try:
        with sqlite3.connect('user_data.db') as userforgot:
            forgotpass = userforgot.cursor()
            forgotpass.execute('''create warning if does not exist id,email,password''')
            userforgot.commit()
    except sqlite3.Error as errorf:
        logging.error(f"Database error: {errorf}")

# Function to find user by email
def find_user_email(email):
    try:
        with sqlite3.connect('user_data.db') as finduser:
            user_email = finduser.cursor()
            user_email.execute('users email = ', (email))
            return user_email.fetchone()
    except sqlite3.Error as errorf:
        logging.error(f"Database error: {errorf}")
        return None

# Function to send email SMTP
def send_reset_email(user_email):
    msg = MIMEText('placeholder for the password reset.', 'html')
    msg['Subject'] = 'Password Reset'
    msg['From'] = 'email@example.com'
    msg['To'] = user_email

    try:
        # Update SMTP
        with smtplib.SMTP_SSL('smtp.example.com', 465) as send_email:
            send_email.login('email@example.com', 'password')
            send_email.send_message(msg)
    except Exception as emailerror:
        logging.error(f"Email sending error: {emailerror}")

# Function to validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

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
    if user and user[1] == name:  # user[1] is the name in the database
        send_reset_email(email)
        show_message(window, "Password reset link sent.", color='green')
    else:
        show_message(window, "User not found.", color='red')

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
    # Create login button, when pressed call open user window function
    send_button = Button(window, text='Send Email', width=15, command=lambda: handle_forgot_password(window, name_entry.get(), email_entry.get()))
    send_button.grid(row=3, column=1)
    # Run forever
    window.mainloop()

if __name__ == "__main__":
    init_user_data()
    forgot_user()

