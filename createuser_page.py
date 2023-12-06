from tkinter import *
import user_page as uw


# Function to destroy login and open user window
def open_user_window(wind):
    wind.destroy()
    uw.main()


def create_user():
    # create main window
    window = Tk()
    window.title('Facial Feature Augmentation using GAN')
    window.geometry("400x150")
    # Make a label for the window
    Label(window, text="Create User").grid(row=0)
    # Create label user info
    Label(window, text="Name").grid(row=1, column=1)
    Label(window, text="Email").grid(row=2, column=1)
    Label(window, text="Password").grid(row=3, column=1)
    Label(window, text="Verify Password").grid(row=4, column=1)
    Entry(window).grid(row=1, column=2)
    Entry(window).grid(row=2, column=2)
    Entry(window).grid(row=3, column=2)
    Entry(window).grid(row=4, column=2)
    # Create login button, when pressed call open user window function
    button = Button(window, text='Create Account', width=15, command=lambda: open_user_window(window))
    button.grid(row=5, column=2)
    # Run forever
    window.mainloop()
