import os.path
import PIL.Image
import cv2
from PySide6 import QtMultimedia
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QFont, QImage, QPixmap
from PySide6 import QtMultimedia, QtMultimediaWidgets, QtWidgets
from PySide6.QtWidgets import QVBoxLayout
import database_page as cd
import sqlite3
import login_page as lp
import shutil
import Augmentation_Project as ap
filename = ""

''' Work in progress, adding webcam and other layouts
    Webcam partially there.'''


# Make database if not exist
def make_user_database():
    connection = sqlite3.connect('user_data.db')
    user = connection.cursor()
    user.execute('''CREATE TABLE IF NOT EXISTS 'users' (id text, email text, password text, unique(email))''')
    connection.commit()


def open_database(wind):
    wind.destroy()
    cd.main()


def open_login(wind):
    wind.destroy()
    lp.main()


def browse_files(text):
    global filename
    # filename = filedialog.askopenfilename(initialdir="/", title="Select a File", filetypes=[("JPG", "*.jpg "),
    #                                                                                         ("JPEG", "*.jpeg")])
    # filename = QFileDialog.getOpenFileName(tr("Open Image"), "/home/jana", tr("Image Files (*.png *.jpg *.bmp)"))

    # text.config(state='normal')
    # text.insert(INSERT, filename)
    # text.config(state='disabled')
    # return filename


def create_caricature(fname, checked, text_box):
    global filename
    #  copy image
    if fname == '':
        show_message('Error', 'Error: Please upload an image!')
    if checked is False:
        show_message('Error', 'Error: Please check consent box!')
    if not(fname == '') and (checked is True):
        folder = os.path.abspath("./Augmentation_Project/original_images")
        shutil.copy(fname, folder)
        text_box.config(state='normal')
        text_box.delete("1.0", "end")
        text_box.config(state='disabled')
        filename = ''
        # call facial landmarking to update processed photo folder
        ap.Facial_Landmarking.main()
        ap.Augmenting_Features.main()


# Function to show a message
def show_message(message, color):
    message = "<font size=20 color = "+color+">" + message + "</font>"
    message_label = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Warning, "Error Message", message)
    message_label.exec()


def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clear_layout(child.layout())


def open_login_page(window, app, layout):
    clear_layout(layout)
    lp.make_page_layout(window, app, layout)


def add_entrybox(layout, label_name):
    box = QtWidgets.QHBoxLayout()
    entry, answer = QtWidgets.QLabel(label_name+':'), QtWidgets.QLineEdit()
    entry.setAlignment(Qt.AlignRight)
    entry.setMaximumWidth(QtWidgets.QApplication.primaryScreen().size().width()/4)
    answer.setMaximumWidth(QtWidgets.QApplication.primaryScreen().size().width()/4)
    customize_widget(entry, "Times New Roman", 20, 'black', '', '', 200)
    answer.setStyleSheet('background-color : #f6f6f6')
    make_accessible(answer, "Input box for " + label_name, "This is where the" + label_name + " is input into a text box.")
    box.addStretch()
    box.addWidget(entry, Qt.AlignRight)
    box.addWidget(answer, Qt.AlignLeft)
    box.addStretch()
    layout.addLayout(box)
    layout.addStretch()
    return answer.text()


def make_accessible(widget, name, description):
    widget.setAccessibleName(name)
    widget.setAccessibleDescription(description)


def customize_widget(widget, font, font_num, color, background_color, border_color, width):
    if font != '':
        widget.setFont(QFont(font, font_num))
    if background_color == '':
        widget.setStyleSheet('color:' + color)
    if color == '':
        widget.setStyleSheet('background-color:' + background_color)
    if (background_color != '') and (color != ''):
        widget.setStyleSheet('background-color:' + background_color + ';color:' + color + ';border:' + border_color)
    if width != '':
        widget.setFixedWidth(width)
    else:
        return
    return


def make_page_layout(window, app, spacing_box):
    # support high contrast themes
    app.setStyle("Fusion")
    # Create label user page
    page_label = QtWidgets.QLabel("User Page")
    customize_widget(page_label, "Arial", 40, 'black', '', '', '')
    make_accessible(page_label, "User's Main Page", "This is the user's Main Page for our application on Comic Contours.")
    spacing_box.addWidget(page_label, alignment=Qt.AlignHCenter)

    # Add a webcam to the layout
    # box = QtWidgets.QGridLayout()
    grey_label = QtWidgets.QLabel()
    video_widget = QtMultimediaWidgets.QVideoWidget()
    video_widget.resize(640, 480)
    spacing_box.addWidget(grey_label)
    camera = QtMultimedia.QCamera(QtMultimedia.QMediaDevices.defaultVideoInput())
    camera.start()
    capture_session = QtMultimedia.QMediaCaptureSession()
    capture_session.setCamera(camera)
    capture_session.setVideoOutput(video_widget)
    video_widget.show()
    # spacing_box.addWidget
    spacing_box.addWidget(video_widget)
    spacing_box.addWidget(grey_label, 0, 0)

    # Add a forgot password button with improved contrast
    capture_photo_button = QtWidgets.QPushButton("Capture Photo")
    customize_widget(capture_photo_button, "Times New Roman", 20, 'white', 'darkblue', '', '')
    make_accessible(capture_photo_button, "Capture Photo button", "This button takes a picture from webcam.")
    capture_photo_button.setShortcut(Qt.Key_Enter)
    login_button = QtWidgets.QPushButton("Create Caricature")
    customize_widget(login_button, "Times New Roman", 20, 'white', 'darkblue', '', '')
    make_accessible(login_button, "Create Caricature button", "This button makes the caricature.")
    # login_button.clicked.connect(lambda: open_login_page(window, app, spacing_box))
    login_button.setShortcut(Qt.Key_Enter)

    spacing_box.addWidget(capture_photo_button, alignment=Qt.AlignHCenter, stretch=10)
    # spacing_box.addStretch()
    spacing_box.addWidget(login_button, alignment=Qt.AlignRight, stretch=10)

    window.setLayout(spacing_box)


# Create user page window
def main(window, app, layout):
    # database
    make_user_database()
    # create main window
    make_page_layout(window, app, layout)
