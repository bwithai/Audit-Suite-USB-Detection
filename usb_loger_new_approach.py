import os
import sys
import logging
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QDialog, QHBoxLayout, QMessageBox, QMainWindow)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal
from sqlmodel import Session

import utils
from database import crud
from database.db import get_db, create_db_and_tables, archive_db
from tableview import TableView
from utils import stylesheet

# Setup logging
logging.basicConfig(level=logging.DEBUG)


class RegisterDialog(QDialog):
    def __init__(self, username, password, db, parent=None):
        super().__init__(parent)
        self.username = username
        self.password = password
        self.db = db
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Register Page')
        self.setWindowIcon(QIcon('usb_logo.jpg'))

        layout = QVBoxLayout()

        # Header
        header_label = QLabel("\nOnly Admin Can Create New User\n")
        header_label.setObjectName("header")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 30, QFont.Bold))
        layout.addWidget(header_label)

        space_label = QLabel("\n")
        layout.addWidget(space_label)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setText(self.username)
        self.username_input.setFont(QFont("Arial", 20))
        layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setText(self.password)
        self.password_input.setFont(QFont("Arial", 20))
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Register button
        register_button = QPushButton("Register New User")
        register_button.clicked.connect(self.register)
        layout.addWidget(register_button)

        self.setLayout(layout)
        self.resize(700, 300)

    def register(self):
        admin_username = self.username_input.text()
        admin_password = self.password_input.text()
        logging.debug(
            f"Attempting to register with Admin Username: {admin_username}, Admin Password Length: {len(admin_password)}")
        new_username, new_password, re_enter_password = "", "", ""

        user = crud.get_user_by_username(admin_username, self.db)

        if not user:
            QMessageBox.warning(self, "Register", "Please Authenticate as admin.")
            return

        if user.admin and crud.verify_password(admin_password, user.hashed_password):
            new_username, new_password, re_enter_password = self.get_new_credentials()
            if new_username == "admin":
                QMessageBox.warning(self, "Register", "Its a default username")
                return

        elif user.super_admin and crud.verify_password(admin_password, user.hashed_password):
            # super_users = crud.get_super_users(self.db)
            if admin_username != "c3so_admin":
                QMessageBox.warning(self, "Register", "C3SO Admin can't create user")
                return
            new_username, new_password, re_enter_password = self.get_new_credentials()
            if new_username == "c3so_admin":
                QMessageBox.warning(self, "Register", "Its a default username")
                return

        else:
            QMessageBox.warning(self, "Register", "Please Authenticate as admin.")
            return

        if new_password != re_enter_password:
            logging.warning("Password not matched")
            QMessageBox.warning(self, "Register", "Password not matched")
            return

        if new_username is None or new_password is None:
            return  # Cancelled, do nothing

        if not new_username or not new_password:
            logging.warning("Please fill all fields")
            QMessageBox.warning(self, "Register", "Please fill all fields")
            return

        try:
            if user.admin:
                crud.create_user(new_username, new_password, self.db)
            elif user.super_admin:
                crud.create_user(new_username, new_password, self.db, super_admin=True)
            logging.info("Registration successful")
            QMessageBox.information(self, "Register", "Registration successful")
            self.accept()
        except Exception as e:
            logging.exception("Registration failed")
            QMessageBox.warning(self, "Register", f"Registration failed: {str(e)}")

    def get_new_credentials(self):
        # Prompt admin to provide new username and password for the new user
        dialog = NewUserCredentialsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_username = dialog.username_input.text()
            new_password = dialog.password_input.text()
            re_enter_password = dialog.re_enter_password.text()
            return new_username, new_password, re_enter_password
        else:
            return None, None, None


class NewUserCredentialsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Create New User Credentials')
        self.setWindowIcon(QIcon('usb_logo.jpg'))

        layout = QVBoxLayout()

        # Header
        header_label = QLabel("\nCreate New User\n")
        header_label.setObjectName("header")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(header_label)

        space_label = QLabel("\n")
        layout.addWidget(space_label)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("New Username")
        self.username_input.setFont(QFont("Arial", 20))
        layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("New Password")
        self.password_input.setFont(QFont("Arial", 20))
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # Re-Enter Password
        self.re_enter_password = QLineEdit()
        self.re_enter_password.setPlaceholderText("Re-Enter New Password")
        self.re_enter_password.setFont(QFont("Arial", 20))
        self.re_enter_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.re_enter_password)

        # Ok button
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        layout.addWidget(cancel_button)

        self.setLayout(layout)
        self.resize(700, 300)


class ChangePasswordDialog(QDialog):
    def __init__(self, username, db, parent=None):
        super().__init__(parent)
        self.username = username
        self.db = db
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
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFont(QFont("Arial", 20))
        self.username_input.setEchoMode(QLineEdit.Password)
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

        self.re_enter_password = QLineEdit()
        self.re_enter_password.setPlaceholderText("Re-Enter New Password")
        self.re_enter_password.setFont(QFont("Arial", 20))
        self.re_enter_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.re_enter_password)

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
        re_enter_password = self.re_enter_password.text()
        logging.debug(f"Attempting to change password for Username: {username}")

        if new_password != re_enter_password:
            logging.warning("Re Enter your password")
            QMessageBox.warning(self, "Change Password", "Password not matched")
            return

        if username == "admin" and current_password == "admin":
            logging.warning("Warning")
            QMessageBox.warning(self, "Change Password", "Admin password is unchangeable")
            return

        try:
            crud.update_password(username, current_password, new_password, self.db)
            logging.info("Password change successful")
            QMessageBox.information(self, "Change Password", "Password change successful")
            self.accept()
        except Exception as e:
            logging.exception("Password change failed")
            QMessageBox.warning(self, "Change Password", f"Password change failed: {str(e)}")


class UserView(QDialog):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.password_input = None
        self.username_input = None
        self.db = None
        self.initUI()

    def get_db_url(self):
        return self.db_url

    def initUI(self):
        self.setWindowTitle('Login Page')
        self.setWindowIcon(QIcon('usb_logo.jpg'))
        self.db: Session = get_db()

        layout = QVBoxLayout()

        self.setup_header(layout)
        self.setup_inputs(layout)
        self.setup_buttons(layout)

        self.setLayout(layout)
        self.resize(700, 300)

    def setup_header(self, layout):
        header_label = QLabel("\nUSB Logger View\n")
        header_label.setObjectName("header")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setFont(QFont("Arial", 30, QFont.Bold))
        layout.addWidget(header_label)
        layout.addWidget(QLabel("\n"))  # Adding space

    def setup_inputs(self, layout):

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setFont(QFont("Arial", 20))
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setFont(QFont("Arial", 20))
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

    def setup_buttons(self, layout):
        buttons_layout = QHBoxLayout()

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        buttons_layout.addWidget(login_button)

        register_button = QPushButton("Register")
        register_button.clicked.connect(self.register)
        buttons_layout.addWidget(register_button)

        change_password_button = QPushButton("Change Password")
        change_password_button.clicked.connect(self.change_password)
        buttons_layout.addWidget(change_password_button)

        layout.addLayout(buttons_layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        logging.debug(f"Attempting to login with Username: {username}")

        if (username == "admin" and password == "admin") or (username == "c3so_admin" and password == "c3so_admin"):
            logging.warning("Invalid username or password")
            QMessageBox.warning(self, "Login", "Invalid username or password")
            return

        try:
            user = crud.login_user(username, password, self.db)
            if user:
                logging.info("Login successful")
                self.accept()
                self.show_table_view(super_admin=user.super_admin, admin=user.admin, db=self.db)
            else:
                logging.warning("Invalid username or password")
                QMessageBox.warning(self, "Login", "Invalid username or password")
        except Exception as e:
            logging.exception("Login failed")
            QMessageBox.warning(self, "Login", f"Login failed: {str(e)}")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        logging.debug(f"Opening Register dialog with Username: {username}")

        dialog = RegisterDialog(username, password, self.db, self)
        if dialog.exec_() == QDialog.Accepted:
            logging.info("Registration dialog accepted")

    def change_password(self):
        username = self.username_input.text()
        logging.debug(f"Opening Change Password dialog with Username: {username}")

        dialog = ChangePasswordDialog(username, self.db, self)
        if dialog.exec_() == QDialog.Accepted:
            logging.info("Change Password dialog accepted")

    def show_table_view(self, db: Session, super_admin: bool = False, admin: bool = False):
        dialog = TableView(super_admin, admin, db)
        dialog.show()
        dialog.exec_()


if __name__ == '__main__':
    create_db_and_tables()
    db: Session = get_db()
    crud.create_user('admin', 'admin', db)
    crud.create_user('c3so_admin', 'c3so_admin', db, super_admin=True)
    app = QApplication(sys.argv)
    # Sana12.12

    # Apply stylesheet
    app.setStyleSheet(stylesheet)
    ex = UserView()
    ex.show()
    sys.exit(app.exec_())
