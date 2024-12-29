from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox

class AdminPage(QWidget):
    def __init__(self, switch_page_callback, logout_callback, fetch_connected_students_callback):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        self.logout_callback = logout_callback
        self.init_ui()


    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Admin Page")
        layout.addWidget(title)



        # Logout button
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout_callback)
        layout.addWidget(logout_button)

        self.setLayout(layout)

   
    
