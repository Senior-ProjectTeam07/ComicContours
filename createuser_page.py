import user_page as up
import login_page as lp
from PySide6.QtWidgets import QPushButton, QApplication, QHBoxLayout, QLabel, QLineEdit, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QImage, QPixmap
import bcrypt
import sqlite3
import re


# Database
def make_user_database():
    connection = sqlite3.connect('user_data.db')
    user = connection.cursor()
    user.execute('''CREATE TABLE IF NOT EXISTS 'users' (id text, email text, password text, unique(email))''')
    connection.commit()


# Function to hash a password
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


# Function to add a new user to the database
def add_user_data(name, email, hashed_password):
    conn = sqlite3.connect('user_data.db')
    new_user = conn.cursor()
    try:
        new_user.execute("INSERT Into users VALUES(?,?,?)", [name, email, hashed_password])
    except sqlite3.Error:
        show_message("Error: Email already in use", "red")
        return False
    conn.commit()
    conn.close()
    return True


# Function to validate email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


# Function to validate password strength
def is_password_strong(password):
    # Set special characters that are acceptable
    special_char = "!@#$%^&*()_+-=<>?"
    # checks to see if length greater or equal to 8
    # any character in password is digit, uppercase, lowercase, and special character
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not(any(char.isdigit() for char in password)):
        return False, "Password must contain a digit"
    if not(any(char.isupper() for char in password)):
        return False, "Password must contain a lowercase letter"
    if not(any(char.islower() for char in password)):
        return False, "Password must contain an uppercase letter"
    if not(any(char in special_char for char in password)):
        return False, "Password must contain a special character"
    return True, ""


# Function to show a message
def show_message(message, color):
    message = "<font size=20 color = + "+color+">" + message + "</font>"
    message_label = QMessageBox(QMessageBox.Icon.Warning, "Error Message", message)
    message_label.exec()


# Modified function to create account
def create_account(win, name, email, password, verify_password):
    print(name, email, password, verify_password)
    is_strong, message = is_password_strong(password)
    hashed_password = hash_password(password)
    if name == '' and email == '' and password == '' and verify_password == '':
        show_message("Please fill in all fields.", "red")
    elif not is_valid_email(email):
        show_message("Invalid email format.", "red")
    elif is_strong is False:
        show_message(message, "red")
    elif password != verify_password:
        show_message("Passwords do not match.", "red")
    elif add_user_data(name, email, hashed_password):
        show_message("Account successfully created.", "green")
        # up.main()
        return
    else:
        show_message("Email already in use.", "red")


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
    return answer


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

    page_label = QLabel("Create Account")
    customize_widget(page_label, "Arial", 40, 'black', '', '', '')
    make_accessible(page_label, "Create Account Page", "This is a Create Account Page for our application on Comic Contours.")
    spacing_box.addWidget(page_label, alignment=Qt.AlignHCenter)
    spacing_box.addStretch()

    # Add a name, email, password, verify password label and input field
    name = add_entrybox(spacing_box, "Name")
    email = add_entrybox(spacing_box, "Email")
    password = add_entrybox(spacing_box, "Password")
    verify_password = add_entrybox(spacing_box, "Verify Password")

    # Add a return to login page button with improved contrast
    spacing_box.addStretch()
    login_button = QPushButton("Return to login page")
    customize_widget(login_button, "Times New Roman", 20, 'blue', 'white', 'white', '')
    make_accessible(login_button, "Return to Login Page button", "This button takes the user into the login page.")
    login_button.clicked.connect(lambda: open_login_page(window, app, spacing_box))
    login_button.setShortcut(Qt.Key_Enter)
    spacing_box.addWidget(login_button, alignment=Qt.AlignLeft, stretch=10)

    # Add a create account button
    create_button = QPushButton("Create Account")
    customize_widget(create_button, "Times New Roman", 20, 'white', 'darkblue', '', '')
    make_accessible(create_button, "Create Account button", "This button creates account for the user.")
    create_button.clicked.connect(lambda: create_account(window, name.text(), email.text(), password.text(), verify_password.text()))
    create_button.setShortcut(Qt.Key_Enter)
    spacing_box.addWidget(create_button)

    window.setLayout(spacing_box)


# Create login window
def main(window, app, layout):
    # database
    make_user_database()
    # create main window
    make_page_layout(window, app, layout)
