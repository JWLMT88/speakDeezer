import auth
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QFileDialog,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import qtstyles


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # set window title and icon
        self.setWindowTitle('Login/Register')
        self.setWindowIcon(QIcon('icon.png'))

        # create a label widget with a custom font
        label = QLabel('Please Login or Register')
        font = QFont('Arial', 20, QFont.Bold)
        label.setFont(font)

        # create username input field with placeholder text and font
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Username')
        self.username_input.setFont(QFont('Arial', 16))

        # create password input field with placeholder text, font and password mask
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Password')
        self.password_input.setFont(QFont('Arial', 16))
        self.password_input.setEchoMode(QLineEdit.Password)

        # create login button with custom colors and font
        login_button = QPushButton('Login')
        login_button.setStyleSheet('background-color: #008CBA; color: white; font-weight: bold; font-size: 16px')
        login_button.setFont(QFont('Arial', 16))
        login_button.clicked.connect(self.login)

        # create register button with custom colors and font
        register_button = QPushButton('Register')
        register_button.setStyleSheet('background-color: #4CAF50; color: white; font-weight: bold; font-size: 16px')
        register_button.setFont(QFont('Arial', 16))
        register_button.clicked.connect(self.register)

        # create a vertical layout with spacing and alignment
        vbox = QtWidgets.QVBoxLayout()
        vbox.setSpacing(30)
        vbox.setAlignment(Qt.AlignCenter)

        # add widgets to the layout with horizontal alignment
        vbox.addWidget(label, alignment=Qt.AlignCenter)
        vbox.addWidget(self.username_input, alignment=Qt.AlignCenter)
        vbox.addWidget(self.password_input, alignment=Qt.AlignCenter)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(50)
        hbox.addWidget(login_button)
        hbox.addWidget(register_button)

        vbox.addLayout(hbox)

        # set the layout for the window and center it on the screen
        self.setLayout(vbox)
        self.setGeometry(0, 0, 500, 300)
        self.move(QtWidgets.QApplication.desktop().screen().rect().center() - self.rect().center())
        # show the window
        self.show()



    def login(self):
        # get username and password input
        username = self.username_input.text()
        password = self.password_input.text()

        # attempt to log in user
        if auth.login(username, password):
            # if successful, show success message
            QtWidgets.QMessageBox.information(self, 'Login successful', f'Logged in as {username}')
        else:
            # if unsuccessful, show error message
            QtWidgets.QMessageBox.warning(self, 'Login failed', 'Incorrect username or password')

    def register(self):
        # get username and password input
        username = self.username_input.text()
        password = self.password_input.text()

        # attempt to register user
        if auth.register(username, password):
            # if successful, show success message
            QtWidgets.QMessageBox.information(self, 'Registration successful', f'Registered as {username}')
        else:
            # if unsuccessful, show error message
            QtWidgets.QMessageBox.warning(self, 'Registration failed', 'Username already taken')