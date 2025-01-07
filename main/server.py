import os
import socket
import ssl
import threading
from time import time
import sqlite3
import bcrypt
import random
import string
<<<<<<< HEAD
<<<<<<< HEAD
import cv2
import numpy as np
import struct
=======
from threading import Lock
from datetime import datetime
>>>>>>> hachwa
=======
import os
import cv2
import numpy as np
import struct
>>>>>>> origin/hachwa
from server_ui import ServerAdminApp

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 12345
base_dir = os.path.dirname(os.path.abspath(__file__))
cert_path = os.path.join(base_dir, 'certs', 'server.crt')
key_path = os.path.join(base_dir, 'certs', 'server.key')
<<<<<<< HEAD
<<<<<<< HEAD

client_sockets = {}  # Dictionary to store client sockets
=======
client_to_login = {}
client_to_login_lock = Lock()  # Lock for thread-safe access to client_to_login
>>>>>>> hachwa
=======
client_to_login = {}  # Dictionary to map client addresses to login names
client_to_login_lock = threading.Lock()  # Thread-safe access to the dictionary
>>>>>>> origin/hachwa
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
        # Store the client socket in the dictionary
        client_sockets[client_address] = client_socket

        while True:
            # Receive data from the client
            data = client_socket.recv(1024)
            if not data:
                print(f"Debug: No data received from {client_address}. Closing connection.")
                break

            try:
                decoded_data = data.decode()  # Decode data from bytes to string
                print(f"Debug: Received data from {client_address}: {decoded_data}")
            except UnicodeDecodeError as e:
                print(f"Debug: Failed to decode data from {client_address}: {data}. Error: {e}")
                client_socket.send(b"Invalid data encoding.")
                continue

            # Split command and arguments
            command, *args = decoded_data.strip().split(',')
            print(f"Debug: Parsed command: {command}, arguments: {args}")

            if command == "authenticate" and len(args) == 2:
                login_name, password = args
                print(f"Debug: Authenticating user {login_name} from {client_address[0]}")
                response = authenticate_user(login_name, password, client_address[0])
                if "Authentication successful" in response:
                    with client_to_login_lock:  # Thread-safe access
                        client_to_login[client_address] = login_name
            elif command == "register" and len(args) == 2:
                student_name, student_id = args
                login_name = f"{student_name}@{student_id}"
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                print(f"Debug: Registering user {student_name} with ID {student_id}. Generated login: {login_name}")
                response = save_to_db(student_name, student_id, login_name, password)
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> origin/hachwa
            elif command == "screenshot":
                # Receive image size (encoded as 4 bytes)
                image_size_data = receive_all(client_socket, 4)
                image_size = struct.unpack(">L", image_size_data)[0]

                # Receive image data
                image_data = receive_all(client_socket, image_size)

                # Decode image
                image = np.frombuffer(image_data, dtype=np.uint8)
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)

                # Display screenshot (optional)
                cv2.imshow("Received Screenshot", image)
<<<<<<< HEAD
                cv2.waitKey(0)
                cv2.destroyAllWindows()

                # Send confirmation to client
                client_socket.send(b"Screenshot received successfully.")
=======
>>>>>>> hachwa
=======
                cv2.waitKey(0) 
                cv2.destroyAllWindows() 

                # Send confirmation to client
                client_socket.send(b"Screenshot received successfully.")
>>>>>>> origin/hachwa

            elif command == "send_file" and len(args) == 1:
                file_name = args[0]
                print(f"Debug: Preparing to receive file {file_name} from {client_address[0]}.")

                # Retrieve the login_name for the client
                with client_to_login_lock:  # Thread-safe access
                    login_name = client_to_login.get(client_address)
                    if not login_name:
                        print(f"Debug: Client {client_address} is not authenticated.")
                        client_socket.send("ERROR:NOT_AUTHENTICATED".encode())
                        continue

                print(f"Debug: login_name for {client_address} is {login_name}")  # Debug statement

                # Receive the file size
                file_size_data = client_socket.recv(1024).decode()
                print(f"Debug: Received file size data: {file_size_data}")
                try:
                    file_size = int(file_size_data)
                    print(f"Debug: Parsed file size: {file_size}")
                except ValueError:
                    print(f"Debug: Invalid file size received: {file_size_data}")
                    response = "Invalid file size."
                    client_socket.send(response.encode())
                    continue

                # Receive the file
                response = receive_file(client_socket, file_name, file_size, client_address[0], login_name)
            else:
                print(f"Debug: Invalid command or arguments received: {decoded_data}")
                response = "Invalid command or arguments."

            # Send response back to the client
            print(f"Debug: Sending response to {client_address}: {response}")
            client_socket.send(response.encode())

    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        with client_to_login_lock:  # Thread-safe access
            
            client_socket.close()
        print(f"Connection with {client_address} closed.")

<<<<<<< HEAD
<<<<<<< HEAD

def receive_file(client_socket, file_name, file_size, client_ip):
=======
def receive_file(client_socket, file_name, file_size, login_name):
>>>>>>> hachwa
=======
def receive_file(client_socket, file_name, file_size, client_ip, login_name):
>>>>>>> origin/hachwa
    """Receive a file from the client and save it to the student's directory."""
    try:
        print(f"Debug: Start receiving file {file_name} from {client_ip}. Expected size: {file_size} bytes.")
        
        # Construct the destination path for the file
        file_path = os.path.join("students", login_name, os.path.basename(file_name))
        print(f"Debug: Expected file path: {file_path}")  # Debug statement

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        print(f"Debug: Directory created (if it didn't exist): {os.path.dirname(file_path)}")  # Debug statement

        received_size = 0
        with open(file_path, 'wb') as file:
            while received_size < file_size:
                file_data = client_socket.recv(min(4096, file_size - received_size))  # Adjust buffer size
                if not file_data:
                    print("Debug: No more data received from client. Breaking out of loop.")
                    break  # No more data
                print(f"Debug: Received {len(file_data)} bytes.")  # Debug received data
                file.write(file_data)
                received_size += len(file_data)
                print(f"Debug: Total received: {received_size}/{file_size}")

        if received_size == file_size:
            print(f"Debug: File {file_name} received successfully. Total size: {received_size} bytes.")
            return f"File {file_name} received and saved successfully."
        else:
            print(f"Debug: File {file_name} not fully received. Received size: {received_size}/{file_size}")
            return f"Error: Incomplete file received. Received size: {received_size}/{file_size} bytes."

    except Exception as e:
        print(f"Error receiving file {file_name}: {e}")
        return f"Error receiving file: {e}"

<<<<<<< HEAD
<<<<<<< HEAD

=======
>>>>>>> hachwa
=======
    
>>>>>>> origin/hachwa
def screenshot(client_socket):
    try:
        print("[DEBUG] Starting screenshot handling loop.")

        while True:
            print("[DEBUG] Sending 'screenshot' command to the client.")
            client_socket.send(b"screenshot")

            # Receive image size
            print("[DEBUG] Waiting to receive image size from client.")
            image_size_data = receive_all(client_socket, 4)
            if not image_size_data:
                print("[WARNING] No data received for image size. Breaking loop.")
                break

            image_size = struct.unpack(">L", image_size_data)[0]
            print(f"[DEBUG] Image size received: {image_size} bytes.")

            # Receive image data
            print("[DEBUG] Waiting to receive image data from client.")
            image_data = receive_all(client_socket, image_size)
            if not image_data:
                print("[WARNING] No image data received. Breaking loop.")
                break

            print(f"[DEBUG] Image data of {len(image_data)} bytes received.")

            # Decode image
            try:
                print("[DEBUG] Decoding image data.")
                image = np.frombuffer(image_data, dtype=np.uint8)
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)

                if image is None:
                    print("[ERROR] Failed to decode image. Skipping display.")
                    continue

                print("[INFO] Image successfully decoded.")
            except Exception as decode_error:
                print(f"[ERROR] Error decoding image: {decode_error}")
                continue

            # Display screenshot
            cv2.startWindowThread()
            print("[DEBUG] Displaying the received screenshot (optional).")
            cv2.imshow("Received Screenshot", image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            # Send confirmation to client
            print("[DEBUG] Sending confirmation to client.")
            client_socket.send(b"Screenshot received successfully.")

    except Exception as e:
        print(f"[ERROR] Error in screenshot function: {e}")

<<<<<<< HEAD
<<<<<<< HEAD

=======
>>>>>>> origin/hachwa
def receive_all(sock, count):
    """
    Receive exactly 'count' bytes from the socket.
    """
    buf = b''
    while count:
        print(f"[DEBUG] Attempting to receive {count} bytes.")
        newbuf = sock.recv(count)
        if not newbuf:
            print("[WARNING] No data received during 'receive_all'. Returning None.")
            return None
        buf += newbuf
        count -= len(newbuf)
        print(f"[DEBUG] Received {len(newbuf)} bytes, {count} bytes remaining.")
    return buf
<<<<<<< HEAD
=======
>>>>>>> hachwa

=======
>>>>>>> origin/hachwa

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
<<<<<<< HEAD
    admin_app.exec_()
=======
    admin_app.exec_()
<<<<<<< HEAD

__all__ = ['client_to_login', 'start_server', 'handle_client']
>>>>>>> hachwa
=======
>>>>>>> origin/hachwa
