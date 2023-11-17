from tkinter import *
from user_page import user_window

# create main window
window = Tk()
window.title('Facial Feature Augmentation using GAN')
window.geometry("400x150")


# Function to destroy login and open user window
def open_user_window():
    window.destroy()
    user_window()


# Make a label for the window
Label(window, text="Facial Feature Augmentation").grid(row=0)
# Create label user info
Label(window, text="Email").grid(row=1)
Label(window, text="Password").grid(row=2)
Label(window, text="Forgot Password?", font=('Times New Roman', 8)).grid(row=3)
Entry(window).grid(row=1, column=1)
Entry(window).grid(row=2, column=1)
# Create login button, when pressed call open user window function
button = Button(window, text='Login', width=25, command=open_user_window)
button.grid(row=4, column=1)
button = Button(window, text='Create Account', width=15, command=window.destroy)
button.grid(row=5, column=0)
# Run forever
window.mainloop()
