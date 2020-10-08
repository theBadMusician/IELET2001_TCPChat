from assets.config import *
import socket
import threading
import random
import string

SERVER_PORT = 80

client_dict = {}
joke_list = []

with open("assets/jokes.txt", "r") as jokes:
    for line in jokes:
        joke_list.append(line)

def deep_get(_dict, keys, default=None):
    for key in keys:
        if isinstance(_dict, dict):
            _dict = _dict.get(key, default)
        else:
            return default
    return _dict

def create_UID():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def read_one_line(sock):
    """
    Read one line of text from a socket
    :param sock: The socket to read from.
    :return:
    """
    newline_received = False
    message = ""
    while not newline_received:
        character = sock.recv(1).decode()
        if character == '\n':
            newline_received = True
        elif character == '\r':
            pass
        else:
            message += character
    return message

def handle_login_req(client_id, login_req):
    login_parsed = login_req.split(' ', 1)
    username = login_parsed[1]

    # Error handling
    if ' ' in username:
        return "loginerr incorrect username format\n"
    elif any(username in name.values() for name in client_dict.values()):
        return "loginerr username already in use\n"
    else:
        client_dict[client_id]['client_name'] = username
        if DEBUG:
            print("Client dict: " + str(client_dict[client_id]))
        return "loginok\n"


def handle_next_client(connection_socket, client_id):
    command = 'x'
    while command != "":
        command = read_one_line(connection_socket)
        print(f"Client ID '{client_id}': {command}")
        if command == "ping":
            response = "PONG\n"
        elif command == "sync":
            response = "modeok\n"
        elif command.split(' ', 1)[0] == "login":
            response = handle_login_req(client_id, command)
        elif command == "joke":
            response = "joke " + joke_list[random.randint(0, len(joke_list) - 1)]
        else:
            response = "501 Command not implemented or 404 command doesn't exist."
        connection_socket.send(response.encode())

    connection_socket.close()


def start_server():
    welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    welcome_socket.bind(("", SERVER_PORT))
    welcome_socket.listen(1)

    hostname = socket.gethostname()
    HOST_ADDRESS = socket.gethostbyname(hostname)
    print(f"Server ready for client connections at (local IPA) {HOST_ADDRESS}:{SERVER_PORT}")
    need_to_run = True

    while need_to_run:
        connection_socket, client_address = welcome_socket.accept()

        client_id = create_UID()
        while client_id in client_dict.keys():
            client_id = create_UID()
        client_dict[client_id] = {}
        client_dict[client_id]['client_name'] = "Anon-" + client_id

        if DEBUG:
            print("Whole client dict: " + str(client_dict))
        print(f"Client ID '{client_id}' connected.")
        client_thread = threading.Thread(target=handle_next_client,
                                         args=(connection_socket, client_id))
        client_thread.start()

    welcome_socket.close()
    print("Server shutdown")


if __name__ == "__main__":
    start_server()
