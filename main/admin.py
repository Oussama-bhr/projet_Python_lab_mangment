import sys
from PyQt5 import QtWidgets
from Dashboard import Dashboard  # Import the Dashboard class

# Function to create a student directory
def create_student_directory(login_name):
    """
    Creates a directory for the student based on their login_name.
    :param login_name: Student's login name (format: studentname@studentid).
    """
    base_directory = "students_directories"  # Folder to store student directories
    student_directory = os.path.join(base_directory, login_name)

    try:
        if not os.path.exists(base_directory):
            os.makedirs(base_directory)
            print(f"Base directory created: {base_directory}")

        if not os.path.exists(student_directory):
            os.makedirs(student_directory)
            print(f"Directory created for the student: {student_directory}")
        else:
            print(f"Directory already exists for the student: {student_directory}")

    except Exception as e:
        print(f"Error creating directory: {e}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # Open the dashboard
    dashboard = Dashboard()
    dashboard.show()

    sys.exit(app.exec_())
