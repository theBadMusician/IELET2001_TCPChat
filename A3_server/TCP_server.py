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

def handle_login_req(client_id, login_req_parsed):
    username = login_req_parsed[1]

    # Error handling
    if ' ' in username:
        return "loginerr incorrect username format\n"
    elif any(username in name['client_name'] for name in client_dict.values()):
        return "loginerr username already in use\n"

    # Set username in db and send res
    else:
        client_dict[client_id]['client_name'] = username
        if DEBUG:
            print("Client dict: " + str(client_dict[client_id]))
        return "loginok\n"

def handle_msg_req(client_id, msg_req_parsed):
    msg = msg_req_parsed[1]
    try:
        return f"msgok {len(client_dict) - 1}\n", f"msg {client_dict[client_id]['client_name']} {msg}\n"
    except Exception:
        return "msgerror Something happened ¯\\_(ツ)_/¯\n"

def handle_privmsg_req(client_id, msg_req_parsed):
    recipient_msg = msg_req_parsed[1].split(' ', 1)
    recipient = recipient_msg[0]
    msg = recipient_msg[1]

    if not any(recipient in name['client_name'] for name in client_dict.values()) or (any(recipient in name['client_name'] for name in client_dict.values()) and "Anon-" in recipient):
        return "msgerr incorrect recipient\n"
    try:
        return f"msgok 1\n", f"msg {client_dict[client_id]['client_name']} {msg}\n"
    except Exception:
        return "msgerror Something happened ¯\\_(ツ)_/¯\n"


def handle_next_client(connection_socket, client_id):
    command = 'x'
    while command != "":
        command = read_one_line(connection_socket)
        command_parsed = command.split(' ', 1)
        print(f"Client ID '{client_id}': {command}")
        if command == "ping":
            response = "PONG\n"
        elif command == "sync":
            response = "modeok\n"
        elif command_parsed[0] == "login":
            response = handle_login_req(client_id, command_parsed)
        elif command_parsed[0] == "msg":
            response = handle_msg_req(client_id, command_parsed)
            [client_dict[dict_client_id]['socket'].send(response[1].encode()) for dict_client_id in client_dict.keys() if client_id != dict_client_id]
        elif command_parsed[0] == "privmsg":
            recipient = command_parsed[1].split(' ', 1)[0]
            response = handle_privmsg_req(client_id, command_parsed)
            recipient_id = [k for k, v in client_dict.items() if recipient in v['client_name']][0]
            client_dict[recipient_id]['socket'].send(response[1].encode())
        elif command == "joke":
            response = "joke " + joke_list[random.randint(0, len(joke_list) - 1)]
        else:
            response = "501 Command not implemented or 404 command doesn't exist."
        try:
            connection_socket.send(response.encode())
        except AttributeError:
            connection_socket.send(response[0].encode())

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
        client_dict[client_id]['client_address'] = client_address
        client_dict[client_id]['socket'] = connection_socket

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
