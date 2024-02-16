from PySide6.QtWidgets import QPushButton, QApplication, QHBoxLayout, QLabel, QVBoxLayout, QWidget, QLineEdit, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QImage, QPixmap, QIcon
import sys
import createuser_page as cu
import user_page as up
import forgotpassword_page as fp
import bcrypt
import sqlite3


# Make database if not exist
def make_user_database():
    connection = sqlite3.connect('user_data.db')
    user = connection.cursor()
    user.execute('''CREATE TABLE IF NOT EXISTS 'users' (id text, email text, password text, unique(email))''')
    connection.commit()


# Function to verify user credentials
def verify_credentials(email, password):
    # gets hashed password from database
    conn = sqlite3.connect('user_data.db')
    verify_cred = conn.cursor()
    verify_cred.execute("""SELECT password From users Where email=?""", (email,))
    hashed_password = verify_cred.fetchone()
    # if there is a hashed password compare with input password
    if hashed_password:
        # return if input password matches hashed password
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password[0])
    else:
        return False


# Clears layout of window
def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clear_layout(child.layout())


# Open user page
def open_user_window(wind, app, layout):
    # if verify_credentials(email, password):
    clear_layout(layout)
    up.main(wind, app, layout)
    # else:
    #    show_message(win, "Invalid credentials!")


# Open create user page
def open_create_user_window(wind, app, layout):
    clear_layout(layout)
    cu.main(wind, app, layout)


# Open forgot password window
def open_forgot_password_window(wind, app, layout):
    clear_layout(layout)
    fp.make_page_layout(wind, app, layout)


# Function to make every widget accessible
def make_accessible(widget, name, description):
    widget.setAccessibleName(name)
    widget.setAccessibleDescription(description)


# Function to customize widget with font, color, and width
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


# Function to add an entry box
def add_entrybox(layout, label_name):
    box = QHBoxLayout()
    entry, answer = QLabel(label_name+':'), QLineEdit()
    entry.setAlignment(Qt.AlignRight)
    entry.setMaximumWidth(QApplication.primaryScreen().size().width()/4)
    answer.setMaximumWidth(QApplication.primaryScreen().size().width()/4)
    customize_widget(entry, "Times New Roman", 20, 'black', '', '', 180)
    answer.setStyleSheet('background-color : #f6f6f6')
    make_accessible(answer, "Input box for " + label_name, "This is where the" + label_name + " is input into a text box.")
    box.addStretch()
    box.addWidget(entry, Qt.AlignRight)
    box.addWidget(answer, Qt.AlignLeft)
    box.addStretch()
    layout.addLayout(box)
    layout.addStretch()


# Function to show a message
def show_message(message, color):
    message = "<font size=20 color = "+color+">" + message + "</font>"
    message_label = QMessageBox(QMessageBox.Icon.Warning, "Error Message", message)
    message_label.exec()


def make_page_layout(window, app, spacing_box):
    # size window
    screen_size = QApplication.primaryScreen().size()
    screen_width, screen_height = screen_size.width(), screen_size.height()

    # support high contrast themes
    app.setStyle("Fusion")

    # Create label user info
    img_label = QLabel()
    img = QImage("icons/logo_CS426.png")
    pixmap = QPixmap(img.scaledToHeight(screen_height/4))
    img_label.setPixmap(pixmap)
    img_label.setScaledContents(True)
    img_label.setMaximumSize((screen_width-20), (screen_height/4))
    img_label.setMinimumSize((screen_width/4), (screen_height/12))
    make_accessible(img_label, "Comic Contours Image", "This is a image of the name Comic Contours with augmented photos in the background.")
    spacing_box.addWidget(img_label)
    # Made label for login page
    page_label = QLabel("Login Page")
    customize_widget(page_label, "Arial", 40, 'black', '', '', '')
    make_accessible(page_label, "Login Page", "This is a Login Page for our application on Comic Contours.")
    spacing_box.addWidget(page_label, alignment=Qt.AlignHCenter)
    spacing_box.addStretch()

    # Add an email, password label and input field
    add_entrybox(spacing_box, "Email")
    add_entrybox(spacing_box, "Password")

    # Add a forgot password button with improved contrast
    forgot_button = QPushButton("Forgot Password?")
    customize_widget(forgot_button, "Times New Roman", 20, 'blue', 'white', 'white', '')
    make_accessible(forgot_button, "Forgot password button", "This button takes the user into the forgot password page.")
    forgot_button.clicked.connect(lambda: open_forgot_password_window(window, app, spacing_box))
    forgot_button.setShortcut(Qt.Key_Enter)
    spacing_box.addWidget(forgot_button, alignment=Qt.AlignLeft, stretch=10)

    # Add a create account button with improved contrast
    create_button = QPushButton("Create Account")
    customize_widget(create_button, "Times New Roman", 20, 'blue', 'white', 'white', '')
    make_accessible(create_button, "Create Account button", "This button takes the user into the create account page.")
    create_button.clicked.connect(lambda: open_create_user_window(window, app, spacing_box))
    create_button.setShortcut(Qt.Key_Enter)
    spacing_box.addWidget(create_button, alignment=Qt.AlignLeft, stretch=10)

    # Add a login button
    login_button = QPushButton("Login")
    customize_widget(login_button, "Times New Roman", 20, 'white', 'darkblue', '', '')
    make_accessible(login_button, "Login button", "This button logs the user into the application.")
    login_button.clicked.connect(lambda: open_user_window(window, app, spacing_box))
    login_button.setShortcut(Qt.Key_Enter)
    spacing_box.addWidget(login_button)


# Create login window
def main():
    # database
    make_user_database()
    # create main window
    app = QApplication(sys.argv)
    window = QWidget()
    # size window
    window.setWindowTitle('Facial Feature Augmentation using GAN')
    screen_size = QApplication.primaryScreen().size()
    screen_width, screen_height = screen_size.width(), screen_size.height()
    window.setGeometry(0, 0, screen_width/4, screen_height/4)
    window.setWindowIcon(QIcon('icons/icon_CS426.png'))
    window.setStyleSheet('background-color: white')
    spacing_box = QVBoxLayout(window)
    window.layout().addChildLayout(spacing_box)
    # make page layout
    make_page_layout(window, app, spacing_box)
    # show window
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
