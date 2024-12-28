from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox

class AdminPage(QWidget):
    def __init__(self, switch_page_callback, logout_callback, fetch_connected_students_callback):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        self.logout_callback = logout_callback
        self.fetch_connected_students_callback = fetch_connected_students_callback
        self.init_ui()


    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Admin Page")
        layout.addWidget(title)

        # Button to view connected students
        view_students_button = QPushButton("View Connected Students")
        view_students_button.clicked.connect(self.view_connected_students)
        layout.addWidget(view_students_button)

        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout_callback)
        layout.addWidget(logout_button)

        self.setLayout(layout)

    def view_connected_students(self):
        """
        Fetch and display the list of connected students.
        """
        try:
            connected_students = self.fetch_connected_students_callback()
            if connected_students:
                student_list = "\n".join(connected_students)
                QMessageBox.information(self, "Connected Students", f"The following students are connected:\n\n{student_list}")
            else:
                QMessageBox.information(self, "Connected Students", "No students are currently connected.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while fetching connected students: {str(e)}")

    
