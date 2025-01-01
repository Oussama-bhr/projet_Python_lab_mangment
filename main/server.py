import os
import socket
import ssl
import threading
from time import time
import sqlite3
import bcrypt
import random
import string
import os
from server_ui import ServerAdminApp

SERVER_HOST = '192.168.111.1'
SERVER_PORT = 12345
base_dir = os.path.dirname(os.path.abspath(__file__))
cert_path = os.path.join(base_dir, 'certs', 'server.crt')
key_path = os.path.join(base_dir, 'certs', 'server.key')

failed_attempts = {}
STUDENT_DIR_ROOT = "students"


def create_student_directory(login_name):
    """Create a directory for a student if it doesn't exist."""
    directory_path = os.path.join(STUDENT_DIR_ROOT, login_name)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory created for student: {directory_path}")
    else:
        print(f"Directory already exists for student: {directory_path}")


def hash_password(password):
    """Hash the password before saving."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(stored_password, provided_password):
    """Verify provided password with stored hashed password."""
    return bcrypt.checkpw(provided_password.encode(), stored_password.encode())


def save_to_db(student_name, student_id, login_name, password, role='student'):
    """Save student credentials to the database."""
    conn = sqlite3.connect("clients.db")
    cursor = conn.cursor()
    try:
        hashed_password = hash_password(password)
        cursor.execute(
            "INSERT INTO clients (student_name, student_id, login_name, password, role) VALUES (?, ?, ?, ?, ?)",
            (student_name, student_id, login_name, hashed_password, role)
        )
        conn.commit()
        create_student_directory(login_name)
        return f"Registration successful. Login Name: {login_name}, Password: {password}"
    except sqlite3.IntegrityError:
        return f"Credentials for {login_name} already exist."
    finally:
        conn.close()


def authenticate_user(login_name, provided_password, client_ip):
    """Authenticate an existing user."""
    conn = sqlite3.connect("clients.db")
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT password FROM clients WHERE login_name = ?", (login_name,))
        result = cursor.fetchone()
        if result is None:
            return "Authentication failed. User not found."

        stored_password = result[0]
        if verify_password(stored_password, provided_password):
            return "Authentication successful"

        return "Authentication failed. Wrong password."
    finally:
        conn.close()


def handle_client(client_socket, client_address):
    """Handle individual client connection."""
    print(f"Connection from {client_address} established.")
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            command, *args = data.strip().split(',')

            if command == "authenticate" and len(args) == 2:
                login_name, password = args
                response = authenticate_user(login_name, password, client_address[0])
            elif command == "register" and len(args) == 2:
                student_name, student_id = args
                login_name = f"{student_name}@{student_id}"
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                response = save_to_db(student_name, student_id, login_name, password)
            else:
                response = "Invalid command or arguments."

            client_socket.send(response.encode())

    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"Connection with {client_address} closed.")


def start_server():
    """Start the SSL server."""
    os.makedirs(STUDENT_DIR_ROOT, exist_ok=True)

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}...")

    secure_socket = context.wrap_socket(server_socket, server_side=True)

    while True:
        client_socket, client_address = secure_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()


if __name__ == "__main__":
    admin_app = ServerAdminApp()
    admin_app.admin_authenticated.connect(start_server)
    admin_app.exec_()
