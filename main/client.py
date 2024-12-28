import socket
import ssl

HOST = '127.0.0.1' 
PORT = 12345   

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE

def connect_to_server(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket = context.wrap_socket(client_socket, server_hostname="localhost")

    try:
        client_socket.connect((HOST, PORT))
        client_socket.send(data.encode())
        response = client_socket.recv(1024).decode()
        print("Server Response:", response)
        return response

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client_socket.close()

# Register a new student
def register():
    student_name = input("Enter student name: ")
    student_id = input("Enter student ID: ")
    data = f"register,{student_name},{student_id}"
    connect_to_server(data)

# Authenticate an existing student
def authenticate():
    attempts = 0
    while attempts < 3:
        login_name = input("Enter your login name: ")
        password = input("Enter your password: ")
        data = f"authenticate,{login_name},{password}"
        response = connect_to_server(data)

        if response is None:
            print("Server not responding. Please try again later.")
            return

        if "Authentication successful" in response:
            print(response)
            return  # Exit to main menu or proceed to post-login menu
        elif "You have been blocked" in response:
            print(response)  # Show the server message directly
            return  # Exit to main menu
        elif "You have failed 3 times" in response:
            print(response)  # Show the server message directly
            return
        else:
            print("Authentication failed. Please try again.")
            attempts += 1  # Increment attempts only after a failed attempt

    if attempts == 3:
        print("You have failed 3 times. Notifying the server.")
        data = f"failed_attempt,{login_name}"  
        connect_to_server(data)


# Main function to manage client operations
def main():
    while True:
        print("\n1. Register")
        print("2. Authenticate")
        print("3. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            register()
        elif choice == '2':
            authenticate()
        elif choice == '3':
            print("Exiting. Goodbye!")
            break
        else:
            print("Invalid option. Please select again.")

if __name__ == "__main__":
    main()
