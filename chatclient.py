# Michael Ha
# ICS 460-01
# Professor Armitage
# 07/25/2023
# Assignment 3 Chat Program
import socket
import sys
import threading
import time

# Constraints
BUFFER_SZ = 2048
exit_flag = False


# Function to print a divider for cleaner chat output
def print_divider():
    print("-" * 40)

# Thread function to continuously receive and print messages from the server
def receive_messages(s):
    global exit_flag
    while not exit_flag:
        try:
            message = s.recv(BUFFER_SZ).decode('utf-8')
            # Handle different types of server messages
            if message == "EXIT_ACK":
                print("Exiting chat...")
                s.close()
                sys.exit()
            elif not message:
                print("Disconnected from server.")
                s.close()
                sys.exit()
            print("\n" + message)
            time.sleep(0.2)  # Adds a slight delay to ensure divider prints after the message
            print_divider()
            print("\nChoose operation (PM, DM, EX): ", end="")
        except OSError as e:
            if exit_flag:
                print("Exiting chat...")
                sys.exit()
            else:
                print(f"Unexpected error: {e}")
                sys.exit()


def main():
    # Ensure correct usage of the client script
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <Server_Name> <Port> <Username>")
        sys.exit()

    # Extract command-line arguments
    server_name, port, username = sys.argv[1], int(sys.argv[2]), sys.argv[3]

    # Set up client socket and connect to the specified server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((server_name, port))
    except:
        print("Connection Error!")
        sys.exit()

    # Send username to the server
    s.send(username.encode('utf-8'))
    server_response = s.recv(BUFFER_SZ).decode('utf-8')

    # Handle server responses for authentication or registration
    if server_response == "PASSWORD":
        print(f"Enter password for {username}: ", end="")
    elif server_response == "REGISTER":
        print(f"Register a password for {username}: ", end="")
    password = input()
    s.send(password.encode('utf-8'))

    auth_status = s.recv(BUFFER_SZ).decode('utf-8')
    # Confirm authentication or registration status
    if auth_status == "AUTH_SUCCESS":
        print("Authentication successful!")
    elif auth_status == "REGISTRATION_SUCCESS":
        print("Registration successful!")
    elif auth_status == "AUTH_FAIL":
        print("Authentication failed!")
        s.close()  # Close the client socket
        sys.exit()

    # Start a thread for receiving messages from the server
    recv_thread = threading.Thread(target=receive_messages, args=(s,), name="ReceiveThread")
    recv_thread.start()

    # Main loop to get user input and send operations to the server
    while True:
        print("Choose operation (PM, DM, EX): ", end="")
        operation = input().upper()

        # Handle public messages
        if operation == "PM":
            print("Enter your message: ", end="")
            message = f"PM:{input()}"
            s.send(message.encode('utf-8'))
            confirmation = s.recv(BUFFER_SZ).decode('utf-8')
            print_divider()
            if confirmation == "BROADCAST_SUCCESS":
                print("Message broadcasted successfully!")
            else:
                print("Error in broadcasting message!")
        # Handle direct/private messages
        elif operation == "DM":
            s.send("LIST_USERS".encode('utf-8'))
            online_users_response = s.recv(BUFFER_SZ).decode('utf-8')
            if online_users_response.startswith("ONLINE_USERS:"):
                online_users = online_users_response.split(":", 1)[1].split(",")
                print_divider()
                print("Online Users: ", ", ".join(online_users))
                print("\nEnter recipient's username from the list above: ", end="")
                recipient = input()
                print("Enter your message: ", end="")
                message = f"DM:{recipient}:{input()}"
                s.send(message.encode('utf-8'))
                confirmation = s.recv(BUFFER_SZ).decode('utf-8')
                print_divider()
                print(confirmation)
        # Handle exit operation
        elif operation == "EX":
            exit_flag = True
            s.send("EX".encode('utf-8'))
            for t in threading.enumerate():
                if t.name == "ReceiveThread":
                    t.join()
            break

    print_divider()
    print("Thank you for using the chat!")


if __name__ == "__main__":
    main()
