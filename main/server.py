import random
import socket
import string
import threading
import sqlite3
import bcrypt
from time import time
import ssl

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345

failed_attempts = {}

# Hash the password before saving
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# Verify provided password with stored hashed password
def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode(), stored_password.encode())

# Save credentials to the database
def save_to_db(student_name, student_id, login_name, password, role='student'):
    conn = sqlite3.connect("clients.db")
    cursor = conn.cursor()

    try:
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO clients (student_name, student_id, login_name, password, role) VALUES (?, ?, ?, ?, ?)",
                       (student_name, student_id, login_name, hashed_password, role))
        conn.commit()
        print(f"Saved {login_name} to the database.")
        return f"Registration successful. Login Name: {login_name}, Password: {password}"
    except sqlite3.IntegrityError:
        return f"Credentials for {login_name} already exist."
    finally:
        conn.close()

# Authenticate an existing user
def authenticate_user(login_name, provided_password, client_ip):
    conn = sqlite3.connect("clients.db")
    cursor = conn.cursor()

    cursor.execute("SELECT password, role FROM clients WHERE login_name = ?", (login_name,))
    result = cursor.fetchone()
    conn.close()

    if client_ip not in failed_attempts:
        failed_attempts[client_ip] = {'count': 0, 'timestamp': time()}

    if failed_attempts[client_ip]['count'] >= 3:
        if time() - failed_attempts[client_ip]['timestamp'] < 300:
            return "You have been blocked due to too many failed attempts. Please try again later."
        else:
            failed_attempts[client_ip] = {'count': 0, 'timestamp': time()}

    if result is None:
        failed_attempts[client_ip]['count'] += 1
        return "Authentication failed. User not found."

    stored_password, role = result
    if verify_password(stored_password, provided_password):
        failed_attempts[client_ip] = {'count': 0, 'timestamp': time()}
        return f"Authentication successful. Role: {role}"
    else:
        failed_attempts[client_ip]['count'] += 1
        if failed_attempts[client_ip]['count'] >= 3:
            failed_attempts[client_ip]['timestamp'] = time()
            return "You have failed 3 times. Please try again later."
        return "Authentication failed. Wrong password."

# Handle client connections
def handle_client(client_socket, client_address):
    print(f"Connection from {client_address} established.")
    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            try:
                command, *args = data.split(',')

                if command == "register" and len(args) == 2:
                    student_name, student_id = args
                    login_name = f"{student_name}@{student_id}"
                    password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                    response = save_to_db(student_name, student_id, login_name, password)

                elif command == "authenticate" and len(args) == 2:
                    login_name, password = args
                    response = authenticate_user(login_name, password, client_address[0])
                    if "Authentication successful" in response:
                        _, role = response.split("Role: ")
                        role = role.strip()
                        if role == "instructor":
                            response = "Welcome Admin! You have full access."
                        elif role == "student":
                            response = "Welcome Student! You have limited access."

                else:
                    response = "Invalid command or arguments."

                client_socket.send(response.encode())
            except ValueError:
                client_socket.send("Invalid input. Use correct format.".encode())

    except Exception as e:
        print(f"Error when handling client {client_address}: {e}")
    finally:
        client_socket.close()
        print(f"Connection with {client_address} closed.")

# Start the server
def start_server():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")

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
    start_server()
