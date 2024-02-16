from PySide6.QtWidgets import QPushButton, QApplication, QHBoxLayout, QLabel, QLineEdit, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QImage, QPixmap
import login_page as lp
import smtplib
import sqlite3
import bcrypt
from email.message import EmailMessage
import secrets
import re


# Make database if not exist
def make_user_database():
    connection = sqlite3.connect('user_data.db')
    user = connection.cursor()
    user.execute('''CREATE TABLE IF NOT EXISTS 'users' (id text, email text, password text, unique(email))''')
    connection.commit()


# Function to find user by email
def find_user_email(email):
    connection = sqlite3.connect('user_data.db')
    find_user = connection.cursor()
    find_user.execute("""SELECT id From users Where email=?""", (email,))
    user_name = find_user.fetchone()[0]
    return user_name


# Function to send email SMTP
def send_reset_email(window, user_email):
    # make new random password
    password_length = 8
    password = secrets.token_urlsafe(password_length)
    # get Name and input new Password into database
    hash_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('user_data.db')
    new_password = conn.cursor()
    try:
        new_password.execute("Update users set password = ? where email = ? ", [hash_password, user_email])
    except sqlite3.Error:
        show_message("Error: No Email Found, Please Create User", "red")
    conn.commit()
    conn.close()
    connection = sqlite3.connect('user_data.db')
    find_user = connection.cursor()
    find_user.execute("""SELECT id From users Where email=?""", (user_email,))
    user_name = find_user.fetchone()[0]
    connection.close()
    # make message
    email_sender = 'seniorproject.faceaugmentation@gmail.com'
    msg = EmailMessage()
    msg['Subject'] = 'Forgot Password'
    msg['From'] = email_sender
    msg['To'] = user_email
    content = 'Hello ' + user_name + ", your new generated password to Facial Feature Augmentation using GAN Software is '" + password + "'. If you are not using the software then please discard this message. Do not reply."
    msg.set_content(content)

    # send message to user
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as send_email:
        send_email.login(email_sender, 'ioyaakqmspzggilz')
        send_email.sendmail(email_sender, user_email, msg.as_string())


# Function to validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


# Function to show a message
def show_message(message, color):
    message = "<font size=20 color = "+color+">" + message + "</font>"
    message_label = QMessageBox(QMessageBox.Icon.Warning, "Error Message", message)
    message_label.exec()


# Function to handle the forgot password logic
def handle_forgot_password(window, name, email):
    if '' in name and email:
        show_message("Please enter all details.", 'red')
        return
    if not is_valid_email(email):
        show_message("Invalid email format.", 'red')
        return

    user = find_user_email(email)
    if user and (user == name):
        send_reset_email(window, email)
        show_message("New password sent to email.", 'green')
    else:
        show_message("User not found.", 'red')


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
    box = QHBoxLayout()
    entry, answer = QLabel(label_name+':'), QLineEdit()
    entry.setAlignment(Qt.AlignRight)
    entry.setMaximumWidth(QApplication.primaryScreen().size().width()/4)
    answer.setMaximumWidth(QApplication.primaryScreen().size().width()/4)
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


# Function to create user
def make_page_layout(window, app, spacing_box):
    # size window
    screen_size = QApplication.primaryScreen().size()
    screen_width, screen_height = screen_size.width(), screen_size.height()

    # support high contrast themes
    app.setStyle("Fusion")
    # Create label user info
    img_label = QLabel()
    img = QImage("icons/logo_CS426.png")
    pixmap = QPixmap(img)
    img_label.setPixmap(pixmap)
    img_label.setScaledContents(True)
    img_label.setMaximumSize((screen_width-20), (screen_height/4))
    img_label.setMinimumSize((screen_width/4), (screen_height/12))
    make_accessible(img_label, "Comic Contours Image", "This is a image of the name Comic Contours with augmented photos in the background.")
    spacing_box.addWidget(img_label)

    page_label = QLabel("Forgot Password")
    customize_widget(page_label, "Arial", 40, 'black', '', '', '')
    make_accessible(page_label, "Create Account Page", "This is a Create Account Page for our application on Comic Contours.")
    spacing_box.addWidget(page_label, alignment=Qt.AlignHCenter)
    spacing_box.addStretch()

    # Add an email label and input field
    name = add_entrybox(spacing_box, "Name")
    email = add_entrybox(spacing_box, "Email")

    # Add a return to login page button with improved contrast
    spacing_box.addStretch()
    login_button = QPushButton("Return to login page")
    customize_widget(login_button, "Times New Roman", 20, 'blue', 'white', 'white', '')
    make_accessible(login_button, "Return to Login Page button", "This button takes the user into the login page.")
    login_button.clicked.connect(lambda: open_login_page(window, app, spacing_box))
    login_button.setShortcut(Qt.Key_Enter)
    spacing_box.addWidget(login_button, alignment=Qt.AlignLeft, stretch=10)

    # Add send email button
    send_email_button = QPushButton("Send Email")
    customize_widget(send_email_button, "Times New Roman", 20, 'white', 'darkblue', '', '')
    make_accessible(send_email_button, "Send Email button", "This button sends email for the user to reset password.")
    send_email_button.clicked.connect(lambda: handle_forgot_password(window, name, email))
    send_email_button.setShortcut(Qt.Key_Enter)
    spacing_box.addWidget(send_email_button)

    window.setLayout(spacing_box)


# Create forgot password window
def main(window, app, layout):
    # database
    make_user_database()
    # create main window
    make_page_layout(window, app, layout)
    window.showMaximized()
