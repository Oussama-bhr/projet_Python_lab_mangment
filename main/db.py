import sqlite3
import bcrypt

# Function to hash passwords
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Connect to the database
conn = sqlite3.connect("clients.db")
cursor = conn.cursor()

# Create the clients table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    student_id TEXT NOT NULL,
    login_name TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Add the 'role' column if it doesn't exist
try:
    cursor.execute("ALTER TABLE clients ADD COLUMN role TEXT NOT NULL DEFAULT 'student'")
    print("Role column added successfully.")
except sqlite3.OperationalError:
    print("Role column already exists.")

# Function to create default instructor accounts
def create_default_instructors():
    instructors = [
        {"name": "Instructor One", "student_id": "11111", "login_name": "instructor1@lab.com", "password": "password1"},
        {"name": "Instructor Two", "student_id": "22222", "login_name": "instructor2@lab.com", "password": "password2"},
        {"name": "Instructor Three", "student_id": "33333", "login_name": "instructor3@lab.com", "password": "password3"}
    ]

    for instructor in instructors:
        try:
            hashed_password = hash_password(instructor["password"])
            cursor.execute(
                "INSERT INTO clients (student_name, student_id, login_name, password, role) VALUES (?, ?, ?, ?, ?)",
                (instructor["name"], instructor["student_id"], instructor["login_name"], hashed_password, "instructor")
            )
            conn.commit()
            print(f"Created instructor account: {instructor['login_name']}")
        except sqlite3.IntegrityError:
            print(f"Instructor account {instructor['login_name']} already exists.")

# Create default instructor accounts
create_default_instructors()

# Close the cursor and connection
cursor.close()
conn.close()

print("Database setup completed successfully!")

