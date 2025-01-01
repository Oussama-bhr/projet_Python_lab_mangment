import os
import shutil
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QTreeView, QFileSystemModel,
    QPushButton, QHBoxLayout, QMessageBox, QFileDialog, QAbstractItemView
)
from PyQt5.QtCore import Qt


class CheckableFileSystemModel(QFileSystemModel):
    """
    Custom QFileSystemModel to include checkboxes for items in the file explorer.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.check_states = {}  # Dictionary to track checked states of items

    def data(self, index, role):
        if role == Qt.CheckStateRole and index.column() == 0:
            file_path = self.filePath(index)
            return self.check_states.get(file_path, Qt.Unchecked)
        return super().data(index, role)

    def setData(self, index, value, role):
        if role == Qt.CheckStateRole and index.column() == 0:
            file_path = self.filePath(index)
            self.check_states[file_path] = value
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            return True
        return super().setData(index, value, role)

    def flags(self, index):
        flags = super().flags(index)
        if index.column() == 0:
            flags |= Qt.ItemIsUserCheckable
        return flags


class StudentPage(QWidget):
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

        # File Explorer with Checkboxes
        self.file_tree = QTreeView()
        self.file_model = CheckableFileSystemModel()
        self.file_model.setRootPath(self.personal_folder_path)
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(self.personal_folder_path))
        self.file_tree.setSelectionMode(QAbstractItemView.NoSelection)  # Disable row selection
        self.file_tree.setColumnWidth(0, 250)
        main_layout.addWidget(self.file_tree)

        # Buttons for actions
        button_layout = QHBoxLayout()

        upload_button = QPushButton("Upload Files/Folders")
        upload_button.clicked.connect(self.upload_files_or_folders)
        button_layout.addWidget(upload_button)

        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_selected)
        button_layout.addWidget(delete_button)

        send_button = QPushButton("Send Selected")
        send_button.clicked.connect(self.send_selected)
        button_layout.addWidget(send_button)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_view)
        button_layout.addWidget(refresh_button)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def get_checked_items(self):
        """
        Retrieve all checked items (files and folders) from the file explorer.
        """
        checked_items = []
        for file_path, state in self.file_model.check_states.items():
            if state == Qt.Checked:
                checked_items.append(file_path)
        return checked_items

    def upload_files_or_folders(self):
        """
        Open a dialog to select files or folders to upload.
        """
        # Use a custom dialog to allow selecting both files and folders
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setOption(QFileDialog.ShowDirsOnly, False)  # Show both files and folders
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # Use Qt's dialog for better control

        # Add a button to allow selecting folders
        dialog.setLabelText(QFileDialog.Accept, "Select Files/Folders")

        if dialog.exec_():
            selected_paths = dialog.selectedFiles()
            if selected_paths:
                try:
                    for path in selected_paths:
                        target_path = os.path.join(self.personal_folder_path, os.path.basename(path))
                        if os.path.isfile(path):
                            shutil.move(path, target_path)
                        elif os.path.isdir(path):
                            shutil.move(path, target_path)
                    QMessageBox.information(self, "Upload", "Files/Folders uploaded successfully.")
                    self.refresh_view()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to upload files/folders: {e}")

    def delete_selected(self):
        """
        Delete all checked items.
        """
        checked_items = self.get_checked_items()
        if checked_items:
            reply = QMessageBox.question(self, "Delete Confirmation", f"Are you sure you want to delete {len(checked_items)} items?")
            if reply == QMessageBox.Yes:
                try:
                    for file_path in checked_items:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    QMessageBox.information(self, "Delete", "Selected items deleted successfully.")
                    self.refresh_view()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete items: {e}")
        else:
            QMessageBox.warning(self, "No Selection", "No files or folders selected.")

    def send_selected(self):
        """
        Simulate sending the selected files or folders.
        """
        checked_items = self.get_checked_items()
        if checked_items:
            QMessageBox.information(self, "Send", f"Selected items sent successfully:\n\n{', '.join(checked_items)}")
        else:
            QMessageBox.warning(self, "No Selection", "No files or folders selected.")

    def refresh_view(self):
        """
        Refresh the file explorer view.
        """
        self.file_tree.setRootIndex(self.file_model.index(self.personal_folder_path))
        QMessageBox.information(self, "Refreshed", "File explorer refreshed.")


# Main application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("HomeClient: Manage Files with Checkboxes")
    home_client = StudentPage()
    window.setCentralWidget(home_client)
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())