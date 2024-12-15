import sys
import socket
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Server details
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

# Function to communicate with the server
def connect_to_server(command, data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        client_socket.send(f"{command},{data}".encode())
        response = client_socket.recv(1024).decode()
        return response
    except Exception as e:
        return f"Error: {e}"
    finally:
        client_socket.close()

# Login Page Class
class LoginPage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        title = QLabel("Login")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Login Name Field
        self.login_name_label = QLabel("Enter your login name:")
        self.login_name_input = QLineEdit()
        self.login_name_input.setPlaceholderText("Login Name")
        layout.addWidget(self.login_name_label)
        layout.addWidget(self.login_name_input)

        # Password Field
        self.password_label = QLabel("Enter your password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.login_button.clicked.connect(self.authenticate)

        self.signup_button = QPushButton("Go to Signup")
        self.signup_button.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; border-radius: 5px;")
        self.signup_button.clicked.connect(lambda: self.switch_page_callback("signup"))

        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.signup_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def authenticate(self):
        login_name = self.login_name_input.text()
        password = self.password_input.text()

        if not login_name or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        response = connect_to_server("authenticate", f"{login_name},{password}")

        if "Authentication successful" in response:
            QMessageBox.information(self, "Success", response)
        else:
            QMessageBox.warning(self, "Error", response)

# Signup Page Class
class SignupPage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)

        title = QLabel("Signup")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Student Name Field
        self.name_label = QLabel("Enter student name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        # Student ID Field
        self.id_label = QLabel("Enter student ID:")
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Student ID")
        layout.addWidget(self.id_label)
        layout.addWidget(self.id_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.register_button.clicked.connect(self.register)

        self.login_button = QPushButton("Go to Login")
        self.login_button.setStyleSheet("background-color: #2196F3; color: white; padding: 10px; border-radius: 5px;")
        self.login_button.clicked.connect(lambda: self.switch_page_callback("login"))

        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.login_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def register(self):
        student_name = self.name_input.text()
        student_id = self.id_input.text()

        if not student_name or not student_id:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        # Send registration data to the server
        response = connect_to_server("register", f"{student_name},{student_id}")

        if "Registration successful" in response:
            login_name = response.split("Login Name: ")[1].split(",")[0]
            password = response.split("Password: ")[1]

            # Copy credentials to the clipboard
            clipboard = QApplication.clipboard()
            clipboard.setText(f"Login Name: {login_name}\nPassword: {password}")

            QMessageBox.information(
                self, "Success",
                f"Registration successful!\n\nLogin Name: {login_name}\nPassword: {password}\n\n"
                "Credentials copied to clipboard."
            )
        else:
            QMessageBox.warning(self, "Error", response)

# Main Application Class
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login and Signup Application")
        self.setGeometry(100, 100, 400, 300)

        # Stack to hold multiple pages
        self.pages = QStackedWidget()

        # Create Login and Signup Pages
        self.login_page = LoginPage(self.switch_page)
        self.signup_page = SignupPage(self.switch_page)

        # Add pages to stack
        self.pages.addWidget(self.login_page)
        self.pages.addWidget(self.signup_page)

        # Layout for the main window
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.pages)
        self.setLayout(main_layout)

    def switch_page(self, page_name):
        if page_name == "login":
            self.pages.setCurrentWidget(self.login_page)
        elif page_name == "signup":
            self.pages.setCurrentWidget(self.signup_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
