import sqlite3
import bcrypt
from tkinter import *
import logging
import createuser_page as cu
import user_page as uw
import forgotpassword_page as fp

# Setup logging
logging.basicConfig(filename='user_management.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# Database setup (assuming SQLite)
def init_db():
    try:
        with sqlite3.connect('user_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {e}")

# Function to hash a password using bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Function to verify credentials
def verify_credentials(email, password):
    try:
        with sqlite3.connect('user_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
            hashed_password = cursor.fetchone()
            if hashed_password:
                return bcrypt.checkpw(password.encode(), hashed_password[0])
            return False
    except sqlite3.Error as e:
        logging.error(f"Database query error: {e}")
        return False

# Function to open user window
def open_user_window(wind, email, password):
    if verify_credentials(email, password):
        wind.destroy()
        uw.main(email)
    else:
        error_label = Label(wind, text="Invalid credentials!", fg="red")
        error_label.grid(row=6, column=2)
        wind.after(3000, error_label.destroy)

def open_create_user_window(wind):
    wind.destroy()
    cu.create_user()

def open_forgot_password_window(event):
    window.destroy()
    fp.forgot_user()

def main():
    init_db()  # Initialize the database
    global window
    window = Tk()
    window.title('Facial Feature Augmentation using GAN')
    window.geometry("400x150")

    Label(window, text="Login").grid(row=0, column=0)
    Label(window, text="Email").grid(row=1, column=1)
    Label(window, text="Password").grid(row=2, column=1)
    email_entry = Entry(window)
    email_entry.grid(row=1, column=2)
    password_entry = Entry(window, show="*")
    password_entry.grid(row=2, column=2)

    label = Label(window, text="Forgot Password?", font=('Times New Roman', 8))
    label.bind("<Button-1>", open_forgot_password_window)
    label.grid(row=3, column=1)

    login_button = Button(window, text='Login', width=25, command=lambda: open_user_window(window, email_entry.get(), password_entry.get()))
    login_button.grid(row=4, column=2)

    create_account_button = Button(window, text='Create Account', width=15, command=lambda: open_create_user_window(window))
    create_account_button.grid(row=5, column=1)

    window.mainloop()

if __name__ == "__main__":
    main()


