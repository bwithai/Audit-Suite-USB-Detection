import sys
import logging
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QDialog, QHBoxLayout, QMessageBox, QMainWindow)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, pyqtSignal

from tableview import TableView
from utils import stylesheet

# Setup logging
logging.basicConfig(level=logging.DEBUG)


class RegisterDialog(QDialog):
    def __init__(self, username, password, parent=None):
        super().__init__(parent)
        self.username = username
        self.password = password
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Register Page')
        self.setWindowIcon(QIcon('usb_logo.jpg'))

        layout = QVBoxLayout()

        # Header
        header_label = QLabel("\nRegister New User\n")
        header_label.setObjectName("header")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 30, QFont.Bold))
        layout.addWidget(header_label)

        space_label = QLabel("\n")
        layout.addWidget(space_label)

        # Full Name input
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Full Name")
        self.fullname_input.setFont(QFont("Arial", 20))
        layout.addWidget(self.fullname_input)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setText(self.username)
        self.username_input.setFont(QFont("Arial", 20))
        layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setText(self.password)
        self.password_input.setFont(QFont("Arial", 20))
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Register button
        register_button = QPushButton("Register")
        register_button.clicked.connect(self.register)
        layout.addWidget(register_button)

        self.setLayout(layout)
        self.resize(700, 300)

    def register(self):
        fullname = self.fullname_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        logging.debug(f"Attempting to register with Full Name: {fullname}, Username: {username}")

        if fullname and username and password:
            logging.info("Registration successful")
            QMessageBox.information(self, "Register", "Registration successful")
            self.accept()
        else:
            logging.warning("Please fill all fields")
            QMessageBox.warning(self, "Register", "Please fill all fields")


class ChangePasswordDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Change Password')
        self.setWindowIcon(QIcon('usb_logo.jpg'))

        layout = QVBoxLayout()

        # Header
        header_label = QLabel("\nChange Password\n")
        header_label.setObjectName("header")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 30, QFont.Bold))
        layout.addWidget(header_label)

        space_label = QLabel("\n")
        layout.addWidget(space_label)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setText(self.username)
        self.username_input.setFont(QFont("Arial", 20))
        layout.addWidget(self.username_input)

        # Current Password input
        self.current_password_input = QLineEdit()
        self.current_password_input.setPlaceholderText("Current Password")
        self.current_password_input.setFont(QFont("Arial", 20))
        self.current_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.current_password_input)

        # New Password input
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("New Password")
        self.new_password_input.setFont(QFont("Arial", 20))
        self.new_password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password_input)

        # Change Password button
        change_password_button = QPushButton("Change Password")
        change_password_button.clicked.connect(self.change_password)
        layout.addWidget(change_password_button)

        self.setLayout(layout)
        self.resize(700, 300)

    def change_password(self):
        username = self.username_input.text()
        current_password = self.current_password_input.text()
        new_password = self.new_password_input.text()
        logging.debug(f"Attempting to change password for Username: {username}")

        if current_password and new_password:
            # Here you would add the logic to change the password
            logging.info("Password change successful")
            QMessageBox.information(self, "Change Password", "Password change successful")
            self.accept()
        else:
            logging.warning("Please fill all fields")
            QMessageBox.warning(self, "Change Password", "Please fill all fields")


class UserView(QDialog):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Login Page')
        self.setWindowIcon(QIcon('usb_logo.jpg'))

        layout = QVBoxLayout()

        # Header
        header_label = QLabel("\nEnter Credentials\n")
        header_label.setObjectName("header")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 30, QFont.Bold))
        layout.addWidget(header_label)

        space_label = QLabel("\n")
        layout.addWidget(space_label)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFont(QFont("Arial", 20))
        layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setFont(QFont("Arial", 20))
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Buttons layout
        buttons_layout = QHBoxLayout()

        # Login button
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.showMoreInfo)
        buttons_layout.addWidget(login_button)

        # Register button
        register_button = QPushButton("Register")
        register_button.clicked.connect(self.register)
        buttons_layout.addWidget(register_button)

        # Change Password button
        change_password_button = QPushButton("Change Password")
        change_password_button.clicked.connect(self.change_password)
        buttons_layout.addWidget(change_password_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)
        self.resize(700, 300)

    def showMoreInfo(self):
        # serial_number = "001CC0EC348DF031069F06C5"
        dialog = TableView(self)
        # print(serial_number)
        dialog.exec_()

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        logging.debug(f"Attempting to login with Username: {username}, Password: {password}")

        if username == "admin" and password == "admin":
            logging.info("Login successful")
            self.show_table_view()
        else:
            logging.warning("Invalid username or password")
            QMessageBox.warning(self, "Login", "Invalid username or password")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        logging.debug(f"Opening Register dialog with Username: {username}")

        dialog = RegisterDialog(username, password, self)
        if dialog.exec_() == QDialog.Accepted:
            logging.info("Registration dialog accepted")

    def change_password(self):
        username = self.username_input.text()
        logging.debug(f"Opening Change Password dialog with Username: {username}")

        dialog = ChangePasswordDialog(username, self)
        if dialog.exec_() == QDialog.Accepted:
            logging.info("Change Password dialog accepted")

    def show_table_view(self):
        dialog = TableView()
        dialog.show()
        dialog.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Apply stylesheet
    app.setStyleSheet(stylesheet)
    ex = UserView()
    ex.show()
    sys.exit(app.exec_())
