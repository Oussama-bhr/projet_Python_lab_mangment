# main.py

import sys
from PyQt5.QtWidgets import QApplication
from admin import create_student_directory  # Importing the create_student_directory function
from dashboard import Dashboard  # Importing the Dashboard UI class

def successful_login(login_name):
    """
    This function will be triggered after a successful login.
    It creates the student's directory and opens the dashboard.
    """
    # Create directory for the student after successful login
    create_student_directory(login_name)

    # After directory creation, show the dashboard
    app = QApplication(sys.argv)
    dashboard = Dashboard()
    dashboard.show()
    sys.exit(app.exec_())

# Example usage
if __name__ == "__main__":
    # Simulate a login name (in real use, this would come from a login form)
    login_name = "studentname@studentid"  # Example login name, replace with real data

    # Call successful login function after student logs in
    successful_login(login_name)
