# Michael Ha
# ICS 460-01
# Professor Armitage
# 07/25/2023
# Assignment 3 Chat Program
import socket
import sys
import threading

# Constraints
MAX_CLIENTS = 100
BUFFER_SZ = 2048

clients = []
clients_lock = threading.Lock()  # Lock to synchronize access to the clients list


# Represents a connected client with their connection, address, and username details
class Client:
    def __init__(self, conn, addr, username):
        self.conn = conn
        self.addr = addr
        self.username = username


# Function to print a divider for cleaner chat output
def print_divider():
    print("-" * 40)


# Broadcast a message to all clients except the sender
def broadcast(message, from_client):
    failed_clients = []
    with clients_lock:
        for client in clients:
            if client != from_client:
                try:
                    client.conn.send(message.encode('utf-8'))
                except:
                    failed_clients.append(client)  # Store the failed client for later removal

    # Remove failed clients outside the loop to avoid modifying the list while iterating
    for client in failed_clients:
        with clients_lock:
            clients.remove(client)

    return "BROADCAST_SUCCESS" if not failed_clients else "BROADCAST_FAILURE"


# Send a private message to a specific client
def private_message(message, recipient):
    with clients_lock:
        for client in clients:
            if client.username == recipient:
                try:
                    client.conn.send(message.encode('utf-8'))
                    return "SUCCESS"
                except:
                    # If the recipient's connection drops unexpectedly
                    clients.remove(client)
        return f"FAILURE: User {recipient} not found."


# Handle each client's communication in its own thread
def client_handler(client):
    while True: # Main loop for listening to a client's messages
        try:
            msg = client.conn.recv(BUFFER_SZ).decode('utf-8')
            # Handle different message types (PM for public, DM for private)
            # Public message handling
            if msg.startswith("PM:"):
                broadcast_msg = f"{client.username} (Broadcast): {msg[3:]}"
                status = broadcast(broadcast_msg, client)
                client.conn.send(status.encode('utf-8'))
            # Direct/private message handling
            elif msg.startswith("DM:"):
                parts = msg.split(":", 2)
                if len(parts) > 2:
                    recipient, private_msg = parts[1], parts[2]
                    pm = f"{client.username} (Private): {private_msg}"
                    status = private_message(pm, recipient)
                    client.conn.send(status.encode('utf-8'))
            # Client exit handling
            elif msg == 'EX':
                client.conn.send("EXIT_ACK".encode('utf-8'))
                with clients_lock:
                    clients.remove(client)
                client.conn.close()
                print(f"{client.username} has left the chatroom.")
                break
            # Listing online users handling
            elif msg == 'LIST_USERS':
                with clients_lock:
                    online_users = [c.username for c in clients]
                    client.conn.send(("ONLINE_USERS:" + ",".join(online_users)).encode('utf-8'))
        except:
            # Handle unexpected client disconnections
            with clients_lock:
                clients.remove(client)
            client.conn.close()
            break


# Check if a username is already registered
def is_registered(username):
    with open('users.txt', 'r') as file:
        for line in file.readlines():
            registered_user, _ = line.strip().split(',')
            if registered_user == username:
                return True
    return False


# Validate user's credentials
def check_password(username, password):
    with open('users.txt', 'r') as file:
        for line in file.readlines():
            registered_user, registered_pass = line.strip().split(',')
            if registered_user == username and registered_pass == password:
                return True
    return False


# Add a new user's credentials to the 'database'
def register(username, password):
    with open('users.txt', 'a') as file:
        file.write(f"{username},{password}\n")


# Main server loop: listen for connections, handle authentication, and start client threads
def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <Port>")
        sys.exit()

    port = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(MAX_CLIENTS)

    print_divider()
    print("=== WELCOME TO THE CHATROOM ===")
    print_divider()
    print(f"Waiting for connections. Listening on port {port}")
    print_divider()

    while True: # Main loop for listening to incoming connections
        conn, addr = server_socket.accept()
        username = conn.recv(BUFFER_SZ).decode('utf-8')

        # Handle registration or authentication
        if is_registered(username):
            # Existing user, request password and authenticate
            conn.send("PASSWORD".encode('utf-8'))
            password = conn.recv(BUFFER_SZ).decode('utf-8')
            if check_password(username, password):
                conn.send("AUTH_SUCCESS".encode('utf-8'))
            else:
                conn.send("AUTH_FAIL".encode('utf-8'))
                conn.close()
                print_divider()
                print(f"Failed authentication attempt for {username}")
                print_divider()
                continue
        else:
            # New user, register them
            conn.send("REGISTER".encode('utf-8'))
            password = conn.recv(BUFFER_SZ).decode('utf-8')
            register(username, password)
            conn.send("REGISTRATION_SUCCESS".encode('utf-8'))

        # On successful registration or authentication, add client and start its handler
        new_client = Client(conn, addr, username)
        with clients_lock:
            clients.append(new_client)

        print_divider()
        print(f"{username} has joined the chatroom.")
        print_divider()
        threading.Thread(target=client_handler, args=(new_client,)).start()


if __name__ == "__main__":
    main()
