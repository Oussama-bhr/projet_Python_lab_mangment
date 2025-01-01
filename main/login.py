import sys
import socket
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QStackedWidget, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import ssl
from student import StudentPage


# Backend Configuration
HOST = '192.168.1.101'
PORT = 12345

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

def connect_to_server():
    """
    Function to create a persistent connection to the server.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket = context.wrap_socket(client_socket, server_hostname="localhost")
    
    try:
        client_socket.connect((HOST, PORT))
        return client_socket
    except Exception as e:
        print(f"Error: {e}")
        return None


# Login Page Class
class LoginPage(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        
        self.client_socket = None  # Store the socket connection
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
        """
        Authenticate the user by sending credentials to the backend server.
        """
        login_name = self.login_name_input.text()
        password = self.password_input.text()

        if not login_name or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        if self.client_socket is None:
            self.client_socket = connect_to_server()  # Establish a persistent connection

        if self.client_socket:
            data = f"authenticate,{login_name},{password}"
            print(f"Sending data to server: {data}") 
            self.send_data_to_server(data)  # Send authentication data
        else:
            QMessageBox.warning(self, "Error", "Unable to establish connection.")

    def send_data_to_server(self, data):
        """
        Send data to the server over the persistent connection.
        """
        try:
            self.client_socket.send(data.encode())
            response = self.client_socket.recv(1024).decode()
            self.handle_server_response(response)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error communicating with server: {e}")


    def handle_server_response(self, response):
        """
        Handle the server response after authentication or other operations.
        """
        if "Authentication successful" in response:
            self.switch_page_callback("student")  # Switch to the student page
        else:
            QMessageBox.warning(self, "Error", response)  # Show the error message from the server



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
        """
        Register a new user by sending the data to the backend server.
        """
        student_name = self.name_input.text()
        student_id = self.id_input.text()

        if not student_name or not student_id:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        data = f"register,{student_name},{student_id}"
        client_socket = connect_to_server()  # Establish the connection here

        if client_socket:
            try:
                client_socket.send(data.encode())  # Send data to the server
                response = client_socket.recv(1024).decode()  # Receive the server response
                self.handle_server_response(response)  # Handle the server response
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error communicating with server: {e}")
            finally:
                client_socket.close()  # Close the connection after communication
        else:
            QMessageBox.warning(self, "Error", "Unable to establish connection.")

    def handle_server_response(self, response):
        """
        Handle the server response after registration.
        """
        if response and "Registration successful" in response:
            login_name = response.split("Login Name: ")[1].split(",")[0]
            password = response.split("Password: ")[1]

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
        self.client_socket = None  # Keep the socket in the main window
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login and Signup Application")
        self.setGeometry(100, 100, 400, 300)

        # Stack to hold multiple pages
        self.pages = QStackedWidget()

        # Create pages
        self.login_page = LoginPage(self.switch_page)
        self.signup_page = SignupPage(self.switch_page)
        self.student_page = StudentPage()

        # Add pages to stack (no admin page)
        self.pages.addWidget(self.login_page)
        self.pages.addWidget(self.signup_page)
        self.pages.addWidget(self.student_page)

        # Layout for the main window
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.pages)
        self.setLayout(main_layout)

    def switch_page(self, page_name):
        """Switch between pages based on page name."""
        if page_name == "login":
            self.pages.setCurrentWidget(self.login_page)
        elif page_name == "signup":
            self.pages.setCurrentWidget(self.signup_page)
        elif page_name == "student":
            self.pages.setCurrentWidget(self.student_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
