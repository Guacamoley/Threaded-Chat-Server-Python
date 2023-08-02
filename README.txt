README for Chat Application
Michael Ha
==================================

This directory contains the source files and additional resources for the Chat Application. The application is a basic chat system that allows users to communicate in real-time. Users can send both public and private messages, and a simple authentication mechanism has been added for registered users.

Files Included:
---------------
1. chatclient.py - The client-side script for users to connect to the chat server.
2. chatserver.py - The server-side script responsible for managing connected clients, messages, and user authentication.
3. users.txt - A simple text database that holds registered users' usernames and their respective passwords.
4. A series of screenshots showing the chat server-client is working

Compilation and Running Instructions:
------------------------------------
This application is developed in Python and does not require any compilation. To run the server or client, you just need a Python interpreter.

To run the server:
$ python3 chatserver.py <Port>
Replace `<Port>` with the port number you want the server to listen on (e.g., `5000`).

To run the client:
$ python3 chatclient.py <Server_Name> <Port> <Username>
Replace `<Server_Name>` with the hostname or IP address of the server, `<Port>` with the port number the server is listening on, and `<Username>` with your desired username.

