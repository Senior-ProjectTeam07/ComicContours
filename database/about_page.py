# about_page.py
import os
import sys
# Add the parent directory to the system path to allow module imports from the parent
current_directory = os.path.dirname(os.path.abspath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
# Continue with imports now that the system path has been modified
from tkinterweb import HtmlFrame
from tkinter import *
import database.login_page as lp
import database.user_page as up
import database.database_page as cd
import customtkinter
import webbrowser


def open_login(wind, frame):
    lp.clear_frame(frame)
    frame.destroy()
    lp.create_main_page(wind, frame)


def open_user(wind, frame):
    lp.clear_frame(frame)
    frame.destroy()
    frame = customtkinter.CTkFrame(master=wind, width=300)
    frame.pack(pady=10, padx=0, expand=TRUE, fill='none')
    up.main(wind, frame)


def open_database(wind, frame):
    lp.clear_frame(frame)
    frame.destroy()
    frame = customtkinter.CTkFrame(master=wind, width=300)
    frame.pack(pady=10, padx=0, expand=TRUE, fill='none')
    cd.main(wind, frame)


def main(window, frame):
    mb = Menu(window)
    mb_dropdown = Menu(mb, tearoff=0)
    mb_dropdown.add_command(label="Logout", font=('Times New Roman', 20), command=lambda: open_login(window, frame))
    mb_dropdown.add_command(label="Main Page", font=('Times New Roman', 20), command=lambda: open_user(window, frame))
    mb_dropdown.add_command(label="Database", font=('Times New Roman', 20), command=lambda: open_database(window, frame))
    mb.add_cascade(label="Menu", menu=mb_dropdown)
    window.config(menu=mb)
    frame.destroy()
    frame = customtkinter.CTkFrame(master=window, width=300)
    frame.pack(pady=10, padx=0, expand=TRUE, fill='both')
    customtkinter.CTkLabel(frame, text="Find more at https://comiccontours.com/", font=('Times New Roman', 20)).pack(pady=12, padx=10, side=TOP)
    f = HtmlFrame(frame)
    f.load_website('https://comiccontours.com/')
    f.pack(fill='both', expand=True)
