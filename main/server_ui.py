import sys
import sqlite3
import bcrypt
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QInputDialog, QScrollArea,QTreeView, QFileSystemModel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
import threading

os.environ["QT_QPA_PLATFORM"] = "xcb"



class ServerAdminApp(QWidget):
    admin_authenticated = pyqtSignal(bool)

    def __init__(self, db_path="clients.db"):
        super().__init__()
        self.db_path = db_path
        self.server_thread = None  # Track the server thread
        self.personal_folder_path = "/home/mouhib/lab_managment/projet_Python_lab_mangment/students"
        self.init_ui()

    def init_ui(self):
        """Set up the UI for the admin login panel."""
        self.setWindowTitle("Admin Login")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Title
        title = QLabel("Admin Login")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Admin Login Fields
        self.login_name_label = QLabel("Enter your admin username:")
        self.login_name_input = QLineEdit()
        self.login_name_input.setPlaceholderText("Admin Username")
        layout.addWidget(self.login_name_label)
        layout.addWidget(self.login_name_input)

        self.password_label = QLabel("Enter your admin password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Password")
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Login Button
        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        self.login_button.clicked.connect(self.authenticate_admin)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def authenticate_admin(self):
        """Authenticate admin by checking the database."""
        login_name = self.login_name_input.text()
        password = self.password_input.text()

        if not login_name or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        if self.check_credentials_in_db(login_name, password):
            QMessageBox.information(self, "Success", "Welcome Admin! You have logged in.")
            self.admin_authenticated.emit(True)  # Trigger the server start signal
            self.show_admin_panel()  # Open admin panel window
            self.close()  # Close the login window after successful login
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials or insufficient permissions.")

    def check_credentials_in_db(self, login_name, password):
        """Check the admin's credentials in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = """
            SELECT password FROM clients 
            WHERE login_name = ? AND role = 'instructor'
            """
            cursor.execute(query, (login_name,))
            result = cursor.fetchone()

            conn.close()

            if result:
                stored_password = result[0]
                return bcrypt.checkpw(password.encode(), stored_password.encode())
            return False
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
            return False

    def show_admin_panel(self):
        """Open the admin control panel with the 'Manage Student Folders' button."""
        self.admin_panel = QWidget()
        self.admin_panel.setWindowTitle("Admin Control Panel")
        self.admin_panel.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # New button to start the server 
        start_server_button = QPushButton("Start Server")
        start_server_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        start_server_button.clicked.connect(self.start_server)  # Connect to the start_server function
        layout.addWidget(start_server_button)

        # Manage Student Folders Button
        manage_folders_button = QPushButton("Manage Student Folders")
        manage_folders_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        manage_folders_button.clicked.connect(self.manage_student_folders)
        layout.addWidget(manage_folders_button)

        # New button to list all users
        list_users_button = QPushButton("List All Users")
        list_users_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; border-radius: 5px;")
        list_users_button.clicked.connect(self.list_all_users)
        layout.addWidget(list_users_button)

        
        title_label = QLabel("Admin Control Panel")
        title_label.setFont(QFont("Arial", 16))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.admin_panel.setLayout(layout)
        self.admin_panel.show()

    def list_all_users(self):
        """List all users from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = """
            SELECT login_name FROM clients WHERE role = 'student'
            """
            cursor.execute(query)
            users = cursor.fetchall()

            conn.close()

            if users:
                self.show_user_selection_dialog(users)
            else:
                QMessageBox.warning(self, "No Users", "No students found in the database.")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")

    def show_user_selection_dialog(self, users):
        """Show a dialog to select a user and take actions."""
        user_names = [user[0] for user in users]

        item, ok = QInputDialog.getItem(self, "Select User", "Choose a student:", user_names, 0, False)
        if ok and item:
            self.selected_user = item
            self.show_user_actions()
        else:
            QMessageBox.warning(self, "No Selection", "No user was selected.")

    def show_user_actions(self):
        """Show available actions for the selected user."""
        self.action_window = QWidget()
        self.action_window.setWindowTitle(f"Actions for {self.selected_user}")
        self.action_window.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()
        
        take_screenshot_button = QPushButton("Take Screenshot")
        take_screenshot_button.clicked.connect(self.take_screenshot)
        layout.addWidget(take_screenshot_button)

        block_device_button = QPushButton("Block Device (Keyboard/Mouse)")
        block_device_button.clicked.connect(self.block_device)
        layout.addWidget(block_device_button)

        self.action_window.setLayout(layout)
        self.action_window.show()

    def take_screenshot(self):
        """Placeholder function to take a screenshot from the user's PC."""
        QMessageBox.information(self, "Screenshot", f"Taking a screenshot from {self.selected_user}'s PC.")
        # Actual screenshot logic would go here, potentially involving remote desktop or system interaction.

    def block_device(self):
        """Placeholder function to block a device on the user's PC."""
        device, ok = QInputDialog.getItem(self, "Block Device", "Choose a device to block:", ["Keyboard", "Mouse"], 0, False)
        if ok and device:
            QMessageBox.information(self, "Block Device", f"Blocking {device} on {self.selected_user}'s PC.")
            # Actual logic to block the device would go here.



    def manage_student_folders(self):
        """Load the existing student folders and provide options to create, delete, or view contents."""
        base_path = "/home/mouhib/lab_managment/projet_Python_lab_mangment/students"
        
        # Open a scrollable area to display the folders
        self.folder_management_window = QWidget()
        self.folder_management_window.setWindowTitle("Manage Student Folders")
        self.folder_management_window.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Title for the client folder management
        title = QLabel("Students Folders")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)

        # File Explorer (TreeView)
        self.file_tree = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(base_path)  # Restrict view to personal folder
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(base_path))
        self.file_tree.setColumnWidth(0, 250)
        self.file_tree.doubleClicked.connect(self.open_file_or_folder)
        layout.addWidget(self.file_tree)

        # Buttons for Upload, Download, Refresh, Create and Delete
        button_layout = QHBoxLayout()

        upload_button = QPushButton("Upload File/Folder")
        upload_button.clicked.connect(self.upload_file_or_folder)
        button_layout.addWidget(upload_button)

        download_button = QPushButton("Download Selected")
        download_button.clicked.connect(self.download_selected)
        button_layout.addWidget(download_button)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_view)
        button_layout.addWidget(refresh_button)

        # Add Create and Delete folder buttons
        create_folder_button = QPushButton("Create Student Folder")
        create_folder_button.clicked.connect(self.create_student_folder)
        button_layout.addWidget(create_folder_button)

        delete_folder_button = QPushButton("Delete Selected Folder")
        delete_folder_button.clicked.connect(self.delete_student_folder)
        button_layout.addWidget(delete_folder_button)

        layout.addLayout(button_layout)

        self.folder_management_window.setLayout(layout)
        self.folder_management_window.show()

    def create_student_folder(self):
        """Create a new student folder."""
        student_name, ok = QInputDialog.getText(self, "New Student Folder", "Enter student name:")
        if ok and student_name:
            # Check if the folder already exists
            student_folder_path = os.path.join(self.personal_folder_path, student_name)
            if not os.path.exists(student_folder_path):
                try:
                    os.makedirs(student_folder_path)
                    QMessageBox.information(self, "Folder Created", f"Student folder for '{student_name}' created successfully.")
                    self.refresh_view()  # Refresh the file view after creation
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create folder: {e}")
            else:
                QMessageBox.warning(self, "Error", "Folder already exists.")

    
    def delete_student_folder(self):
        """Delete the selected student folder."""
        index = self.file_tree.currentIndex()
        student_folder_path = self.file_model.filePath(index)
        
        if os.path.isdir(student_folder_path):
            confirm = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete the folder: {student_folder_path}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if confirm == QMessageBox.Yes:
                try:
                    os.rmdir(student_folder_path)  # Use os.rmdir() for empty directories, os.remove() for files
                    QMessageBox.information(self, "Folder Deleted", f"Folder '{student_folder_path}' deleted successfully.")
                    self.refresh_view()  # Refresh the file view after deletion
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete folder: {e}")
        else:
            QMessageBox.warning(self, "Error", "No folder selected or folder is not empty.")

   # Open a file or navigate to a folder
    def open_file_or_folder(self, index):
        file_path = self.file_model.filePath(index)
        if os.path.isdir(file_path):
            self.file_tree.setRootIndex(self.file_model.index(file_path))
        else:
            QMessageBox.information(self, "File Opened", f"Opening file: {file_path}")

# Upload file or folder
    def upload_file_or_folder(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Upload")
        if file_path:
            try:
                target_path = os.path.join(self.personal_folder_path, os.path.basename(file_path))
                os.rename(file_path, target_path)
                QMessageBox.information(self, "Upload", f"Uploaded file to: {target_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to upload file: {e}")

    # Download selected file or folder
    def download_selected(self):
        index = self.file_tree.currentIndex()
        file_path = self.file_model.filePath(index)

        if file_path:
            save_path = QFileDialog.getExistingDirectory(self, "Select Directory to Save Downloaded File/Folder")
            if save_path:
                try:
                    target_path = os.path.join(save_path, os.path.basename(file_path))
                    os.rename(file_path, target_path)
                    QMessageBox.information(self, "Download", f"Downloaded: {file_path}\nTo: {target_path}")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to download file: {e}")
        else:
            QMessageBox.warning(self, "Error", "No file or folder selected.")

    # Refresh the file explorer view
    def refresh_view(self):
        self.file_tree.setRootIndex(self.file_model.index(self.personal_folder_path))
        QMessageBox.information(self, "Refreshed", "File explorer refreshed.")


    def start_server(self):
        """Trigger the server start logic in a new thread."""
        QMessageBox.information(self, "Server", "The server is starting in the background.")

        if self.server_thread and self.server_thread.is_alive():
            QMessageBox.warning(self, "Server", "The server is already running.")
            return

        # Start the server in a separate thread to avoid blocking the main thread
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True  # Make the thread a daemon thread
        self.server_thread.start()

    def run_server(self):
        """Run the server logic."""
        try:
            from server import start_server
            start_server()
        except Exception as e:
            print(f"Server Error: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    server_admin_app = ServerAdminApp()
    server_admin_app.show()
    sys.exit(app.exec_())