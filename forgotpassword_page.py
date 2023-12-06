from tkinter import *
import login_page as lp


# Function to destroy login and open user window
def open_login_window(wind):
    wind.destroy()
    lp.login_window()


def forgot_user():
    # create main window
    window = Tk()
    window.title('Facial Feature Augmentation using GAN')
    window.geometry("400x150")
    # Make a label for the window
    Label(window, text="Forgot Password").grid(row=0, column=0)
    # Create label user info
    Label(window, text="Name").grid(row=1, column=1)
    Label(window, text="Email").grid(row=2, column=1)
    Entry(window).grid(row=1, column=2)
    Entry(window).grid(row=2, column=2)
    # Create login button, when pressed call open user window function
    button = Button(window, text='Send Password', width=15, command=lambda: open_login_window(window))
    button.grid(row=3, column=2)
    button = Button(window, text='Login Page', width=10, command=lambda: open_login_window(window))
    button.grid(row=4, column=1, columnspan=1)
    # Run forever
    window.mainloop()
