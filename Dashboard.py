import os
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class DirectoryContentWindow(QWidget):
    """
    A new window to display the content of a selected directory.
    """

    def __init__(self, directory_path):
        super().__init__()
        self.setWindowTitle(f"Content of {os.path.basename(directory_path)}")
        self.resize(400, 300)

        layout = QVBoxLayout()

        # Fetch and display the directory content
        try:
            content = os.listdir(directory_path)
            if not content:
                label = QLabel("The directory is empty.")
                label.setAlignment(Qt.AlignCenter)
                layout.addWidget(label)
            else:
                for item in content:
                    item_label = QLabel(item)
                    item_label.setFont(QFont("Arial", 12))
                    layout.addWidget(item_label)
        except Exception as e:
            error_label = QLabel(f"Error: {str(e)}")
            layout.addWidget(error_label)

        self.setLayout(layout)


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.resize(800, 600)

        # Main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Title label
        title_label = QLabel("List of Directories")
        title_label.setFont(QFont("Arial", 16))
        title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title_label)

        # Scroll area for directories and buttons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        self.layout.addWidget(scroll_area)

        # Load directories
        self.load_directories()

    def load_directories(self):
        """
        Dynamically load directories and create "View Content" buttons.
        """
        base_path = "C:\\Users\\Bahri\\projet_Python_lab_mangment\\main\\students_directories"

        # Clear previous items
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Load and display directories
        try:
            directories = [
                d
                for d in os.listdir(base_path)
                if os.path.isdir(os.path.join(base_path, d))
            ]
            if not directories:
                no_dir_label = QLabel("No directories found.")
                no_dir_label.setFont(QFont("Arial", 12))
                no_dir_label.setAlignment(Qt.AlignCenter)
                self.scroll_layout.addWidget(no_dir_label)
            else:
                for directory in directories:
                    dir_path = os.path.join(base_path, directory)

                    # Directory label
                    dir_label = QLabel(directory)
                    dir_label.setFont(QFont("Arial", 12))
                    self.scroll_layout.addWidget(dir_label)

                    # View Content button
                    view_button = QPushButton("View Content")
                    view_button.setFont(QFont("Arial", 10))
                    view_button.clicked.connect(
                    )
                    self.scroll_layout.addWidget(view_button)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load directories: {e}")

    def open_directory_content(self, directory_path):
        """
        Open a new window to display the content of a selected directory.
        """
        self.content_window = DirectoryContentWindow(directory_path)
        self.content_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec())
