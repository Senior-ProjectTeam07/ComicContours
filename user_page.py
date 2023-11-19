from tkinter import *
from tkinter import filedialog
from database_page import create_database
# Function for opening the file explorer window


def browse_files(text):
    filename = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=[("JPG", "*.jpg "),
                                                                                            ("JPEG", "*.jpeg")])
    text.insert(INSERT, filename)


def open_database(wind):
    wind.destroy()
    create_database()


# Create user window
def user_window():
    window = Tk()
    window.title('Facial Feature Augmentation using GAN')
    window.minsize(1000, 200)

    mb = Menu(window)
    mb_dropdown = Menu(mb, tearoff=0)
    mb_dropdown.add_command(label="Logout")
    mb_dropdown.add_command(label="About")
    mb_dropdown.add_command(label="Database", command=lambda: open_database(window))
    mb.add_cascade(label="Menu", menu=mb_dropdown)
    window.config(menu=mb)
    # mb.grid(row=0, column=2, padx=10, pady=5)
    # Make a label for the window
    Label(window, text="Welcome to Facial Feature Augmentation").grid(row=2, column=1, pady=10)
    # Make a button for browsing images the window
    file_text = Text(window, height=1, width=100)
    file_text.grid(row=7, column=1, pady=10, padx=0, sticky=W)
    button = Button(window, text='Upload Image', width=15, command=lambda: browse_files(file_text))
    button.grid(row=7, column=0, pady=10, padx=10, sticky=W)
    # Liability button
    var1 = IntVar()
    Checkbutton(window, text='I consent to having the photo and caricature added to a database for facial recognition research purposes only.',
                variable=var1).grid(row=9, column=1, sticky=W, padx=20)
    # Caricature button
    button = Button(window, text='Create Caricature', width=25)
    button.grid(row=12, column=1, pady=10, padx=10, sticky=E)
    # Run forever
    window.mainloop()
