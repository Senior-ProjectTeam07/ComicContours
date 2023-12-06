from tkinter import *
from user_page import user_window
from createuser_page import create_user
import forgotpassword_page as fp


# Function to destroy login and open user window
def open_user_window(wind):
    wind.destroy()
    user_window()


def open_create_user_window(wind):
    wind.destroy()
    create_user()


def open_login_window(event):
    window.destroy()
    fp.forgot_user()


def login_window():
    global window
    # create main window
    window = Tk()
    window.title('Facial Feature Augmentation using GAN')
    window.geometry("400x150")
    # Make a label for the window
    Label(window, text="Login").grid(row=0, column=0)
    # Create label user info
    Label(window, text="Email").grid(row=1, column=1)
    Label(window, text="Password").grid(row=2, column=1)
    label = Label(window, text="Forgot Password?", font=('Times New Roman', 8))
    label.bind("<Button-1>", open_login_window)
    label.grid(row=3, column=1)
    Entry(window).grid(row=1, column=2)
    Entry(window).grid(row=2, column=2)
    # Create login button, when pressed call open user window function
    button = Button(window, text='Login', width=25, command=lambda: open_user_window(window))
    button.grid(row=4, column=2)
    button = Button(window, text='Create Account', width=15, command=lambda: open_create_user_window(window))
    button.grid(row=5, column=1)
    # Run forever
    window.mainloop()


