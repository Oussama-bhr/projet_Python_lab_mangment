import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTreeView, QFileSystemModel,
    QPushButton, QHBoxLayout, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QDir


class HomeClient(QWidget):
    def __init__(self):
        super().__init__()
        self.personal_folder_path = os.path.join(os.path.expanduser("~"), "MyPersonalSpace")
        self.create_personal_folder()
        self.init_ui()

    def create_personal_folder(self):
        """
        Automatically create a personal folder locally if it doesn't already exist.
        """
        try:
            if not os.path.exists(self.personal_folder_path):
                os.makedirs(self.personal_folder_path)
                print(f"Folder created: {self.personal_folder_path}")
            else:
                print(f"Folder already exists: {self.personal_folder_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create personal folder: {e}")

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("HomeClient: Personal Space")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px 0;")
        main_layout.addWidget(title)

        # File Explorer (TreeView)
        self.file_tree = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(self.personal_folder_path)  # Restrict view to personal folder
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(self.personal_folder_path))
        self.file_tree.setColumnWidth(0, 250)
        self.file_tree.doubleClicked.connect(self.open_file_or_folder)
        main_layout.addWidget(self.file_tree)

        # Buttons for Upload, Download, and Refresh
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

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

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


# Main application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("HomeClient: File Upload & Download")
    home_client = HomeClient()
    window.setCentralWidget(home_client)
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
