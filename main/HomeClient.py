import os
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTreeView, QFileSystemModel,
    QPushButton, QHBoxLayout, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QModelIndex


class CheckableFileSystemModel(QFileSystemModel):
    def __init__(self):
        super().__init__()
        self.checked_files = set()

    def flags(self, index: QModelIndex):
        base_flags = super().flags(index)
        if index.column() == 0:  # Enable checkboxes in the first column
            return base_flags | Qt.ItemIsUserCheckable
        return base_flags

    def data(self, index: QModelIndex, role: int):
        if role == Qt.CheckStateRole and index.column() == 0:
            file_path = self.filePath(index)
            return Qt.Checked if file_path in self.checked_files else Qt.Unchecked
        return super().data(index, role)

    def setData(self, index: QModelIndex, value, role: int):
        if role == Qt.CheckStateRole and index.column() == 0:
            file_path = self.filePath(index)
            if value == Qt.Checked:
                self.checked_files.add(file_path)
            else:
                self.checked_files.discard(file_path)
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
        return super().setData(index, value, role)

    def get_checked_files(self):
        return list(self.checked_files)


class HomeClient(QWidget):
    def __init__(self):
        super().__init__()
        self.personal_folder_path = os.path.join(os.path.expanduser("~"), "MyPersonalSpace")
        self.create_personal_folder()
        self.init_ui()

    def create_personal_folder(self):
        if not os.path.exists(self.personal_folder_path):
            os.makedirs(self.personal_folder_path)

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
        self.file_model = CheckableFileSystemModel()
        self.file_model.setRootPath(self.personal_folder_path)
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(self.personal_folder_path))
        self.file_tree.setColumnWidth(0, 250)
        main_layout.addWidget(self.file_tree)

        # Buttons for Upload, Download, Refresh, Delete, and Logout
        button_layout = QHBoxLayout()

        upload_button = QPushButton("Upload File/Folder")
        upload_button.clicked.connect(self.upload_file_or_folder)
        button_layout.addWidget(upload_button)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_view)
        button_layout.addWidget(refresh_button)

        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_selected)
        button_layout.addWidget(delete_button)

        # Logout button (just for design)
        logout_button = QPushButton("Logout")
        logout_button.setStyleSheet("background-color: lightgray; font-weight: bold;")
        button_layout.addWidget(logout_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def upload_file_or_folder(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Upload Option")
        msg_box.setText("Do you want to upload a file or a folder?")
        file_button = msg_box.addButton("File", QMessageBox.ActionRole)
        folder_button = msg_box.addButton("Folder", QMessageBox.ActionRole)
        cancel_button = msg_box.addButton(QMessageBox.Cancel)

        msg_box.exec_()

        if msg_box.clickedButton() == file_button:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Upload")
            if file_path:
                self.move_to_personal_space(file_path)
        elif msg_box.clickedButton() == folder_button:
            folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Upload")
            if folder_path:
                self.move_to_personal_space(folder_path)

    def move_to_personal_space(self, path):
        try:
            target_path = os.path.join(self.personal_folder_path, os.path.basename(path))
            if os.path.isfile(path):
                os.rename(path, target_path)
            elif os.path.isdir(path):
                os.makedirs(target_path, exist_ok=True)
                for root, dirs, files in os.walk(path):
                    for file in files:
                        src_file = os.path.join(root, file)
                        relative_path = os.path.relpath(root, path)
                        dest_dir = os.path.join(target_path, relative_path)
                        os.makedirs(dest_dir, exist_ok=True)
                        os.rename(src_file, os.path.join(dest_dir, file))
            QMessageBox.information(self, "Upload", f"Uploaded to: {target_path}")
            self.refresh_view()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to upload: {e}")

    def delete_selected(self):
        selected_files = self.file_model.get_checked_files()
        if not selected_files:
            QMessageBox.warning(self, "Error", "No files selected.")
            return

        for file_path in selected_files:
            reply = QMessageBox.question(
                self, "Delete Confirmation",
                f"Are you sure you want to delete '{file_path}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                    elif os.path.isdir(file_path):
                        os.rmdir(file_path)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete file: {e}")

        self.file_model.checked_files.clear()
        self.refresh_view()

    def refresh_view(self):
        self.file_tree.setRootIndex(self.file_model.index(self.personal_folder_path))


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
