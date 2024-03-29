# user_page.py

from tkinter import Tk, Label, Button, E, W, INSERT, Text, filedialog, Checkbutton, BooleanVar, messagebox, Menu
import shutil
import sys
import os
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
import os.path
import database.database_page as cd
import database.login_page as lp
import landmarking.landmark as fl
import augmentation.augment as af

filename = ""

def open_database(wind):
    wind.destroy()
    cd.main()

def open_login(wind):
    wind.destroy()
    lp.main()

def browse_files(text):
    global filename
    filename = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=[("JPG", "*.jpg "),
                                                                                            ("JPEG", "*.jpeg")])
    text.config(state='normal')
    text.insert(INSERT, filename)
    text.config(state='disabled')
    return filename

def create_caricature(fname, checked, text_box):
    global filename
    #  copy image
    if fname == '':
        messagebox.showerror('Error', 'Error: Please upload an image!')
    if checked is False:
        messagebox.showerror('Error', 'Error: Please check consent box!')
    if not(fname == '') and (checked is True):
        folder = os.path.abspath("./data/original_images")
        shutil.copy(fname, folder)
        text_box.config(state='normal')
        text_box.delete("1.0", "end")
        text_box.config(state='disabled')
        filename = ''
        # call facial landmarking to update processed photo folder
        fl.main()
        af.main()

# Create user window
def main():
    global filename
    window = Tk()
    window.title('Facial Feature Augmentation using GAN')
    window.minsize(1000, 200)

    mb = Menu(window)
    mb_dropdown = Menu(mb, tearoff=0)
    mb_dropdown.add_command(label="Logout", command=lambda: open_login(window))
    mb_dropdown.add_command(label="About")
    mb_dropdown.add_command(label="Database", command=lambda: open_database(window))
    mb.add_cascade(label="Menu", menu=mb_dropdown)
    window.config(menu=mb)
    # Make a label for the window
    Label(window, text="Welcome to Facial Feature Augmentation").grid(row=2, column=1, pady=10)
    # Make a button for browsing images the window
    file_text = Text(window, height=1, width=100, state='disabled')
    file_text.grid(row=7, column=1, pady=10, padx=0, sticky=W)
    button = Button(window, text='Upload Image', width=15, command=lambda: (filename == browse_files(file_text)))
    button.grid(row=7, column=0, pady=10, padx=10, sticky=W)
    # Liability button
    checkbutton_var = BooleanVar()
    Checkbutton(window, text='I consent to having the photo and caricature added to a database for facial recognition research purposes only.',
                variable=checkbutton_var).grid(row=9, column=1, sticky=W, padx=20)
    # Caricature button
    button = Button(window, text='Create Caricature', width=25, command=lambda: create_caricature(filename, checkbutton_var.get(), file_text))
    button.grid(row=12, column=1, pady=10, padx=10, sticky=E)
    # Run forever
    window.mainloop()

if __name__ == "__main__":
    main()
