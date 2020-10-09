from assets.config import *
from assets.DebugTools import *
import socket
import threading
import random
import string

SERVER_PORT = 80

client_dict = {}
cmd_list = ['sync', 'async', 'login', 'msg', 'privmsg', 'inbox', 'users', 'joke', 'help']
joke_list = []

with open("assets/jokes.txt", "r") as jokes:
    for line in jokes:
        joke_list.append(line)

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
        try:
            character = sock.recv(1).decode()
        except (ConnectionResetError, ConnectionAbortedError) as e:
            return -1
        if character == '\n':
            newline_received = True
        elif character == '\r':
            pass
        else:
            message += character
    return message

def dc_checkup(client_id):

    for dict_client_id in tuple(client_dict):
        if client_id != dict_client_id:
            try:
                client_dict[dict_client_id]['socket'].send("\r".encode())
                WARNING_PRINT("SENT CHECK TO " + dict_client_id)
            except (ConnectionResetError, ConnectionAbortedError) as e:
                client_dict[dict_client_id]['socket'].close()
        print("<<<<================>")

def dc_handling_cleanup():
    dead_sockets = [k for k, v in client_dict.items() if v['socket'].fileno() == -1]
    for k in dead_sockets:
        client_dict.pop(k, None)
        WARNING_PRINT(f"SOCKET {k} CLOSED")
        print(client_dict)
    dead_sockets.clear()

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
        return "loginok\n"

def handle_msg_req(client_id, msg_req_parsed):
    msg = msg_req_parsed[1]

    response_string = f"msg {client_dict[client_id]['client_name']} {msg}\n"
    try:
        for dict_client_id in client_dict.keys():
            if client_id == dict_client_id:
                continue
            elif client_dict[dict_client_id]['sync_mode']:
                client_dict[dict_client_id]['inbox'].append(response_string)
            else:
                client_dict[dict_client_id]['socket'].send(response_string.encode())
        return f"msgok {len(client_dict) - 1}\n"
    except Exception:
        return "msgerror Something happened ¯\\_(ツ)_/¯\n"

def handle_privmsg_req(client_id, msg_req_parsed):
    recipient_msg = msg_req_parsed[1].split(' ', 1)

    recipient = recipient_msg[0]
    try:
        recipient_id = [k for k, v in client_dict.items() if recipient in v['client_name']][0]
    except IndexError:
        return "msgerr incorrect recipient\n"
    msg = recipient_msg[1]

    response_string = f"privmsg {client_dict[client_id]['client_name']} {msg}\n"

    if client_dict[client_id]['client_name'] == "Anon-" + str(client_id):
        return "msgerr unauthorized\n"
    elif not any(recipient in name['client_name'] for name in client_dict.values()):
        return "msgerr incorrect recipient\n"
    elif recipient == "Anon-" + str(recipient_id):
        return "msgerr incorrect recipient\n"
    elif client_dict[recipient_id]['sync_mode']:
        try:
            client_dict[recipient_id]['inbox'].append(response_string)
            return f"msgok 1\n"
        except Exception:
            return "msgerror Something happened ¯\\_(ツ)_/¯\n"
    else:
        try:
            client_dict[recipient_id]['socket'].send(response_string.encode())
            return f"msgok 1\n"
        except Exception:
            return "msgerror Something happened ¯\\_(ツ)_/¯\n"

def handle_next_client(connection_socket, client_id):
    socket_open = True
    while socket_open:
        command = read_one_line(connection_socket)
        try:
            command_parsed = command.split(' ', 1)
        except AttributeError:
            pass
        print(f"Client ID '{client_id}': {command}")

        if command == -1:
            socket_open = False
            connection_socket.close()
            dc_handling_cleanup()
            continue
        elif command == "sync":
            client_dict[client_id]['sync_mode'] = True
            client_dict[client_id]['inbox'] = []
            response = "modeok\n"
        elif command == "async":
            client_dict[client_id]['sync_mode'] = False
            client_dict[client_id]['inbox'] = []
            response = "modeok\n"
        elif command_parsed[0] == "login":
            dc_checkup(client_id)
            response = handle_login_req(client_id, command_parsed)
        elif command_parsed[0] == "msg":
            dc_checkup(client_id)
            response = handle_msg_req(client_id, command_parsed)
        elif command_parsed[0] == "privmsg":
            dc_checkup(client_id)
            response = handle_privmsg_req(client_id, command_parsed)
        elif command == "inbox":
            client_inbox = client_dict[client_id]['inbox']
            inbox_contents = ''.join([str(elem) for elem in client_inbox])
            response = "inbox " + str(len(client_inbox)) + "\n" + str(inbox_contents)
            client_dict[client_id]['inbox'] = []
        elif command_parsed[0] == "users":
            # TODO: fix the bug of users not updating at once. Maybe w setInterval solution.
            dc_checkup(client_id)
            client_names_list = [v['client_name'] for k, v in client_dict.items()]
            client_names = ' '.join([str(elem) for elem in client_names_list])
            response = "users " + client_names + "\n"
        elif command == "joke":
            joke = joke_list[random.randint(0, len(joke_list) - 1)]
            response = "joke " + joke
        elif command == "help":
            cmds = ' '.join([str(elem) for elem in cmd_list])
            response = "supported " + cmds + "\n"
        else:
            response = "cmderr command not supported"
        connection_socket.send(response.encode())
        """except (ConnectionResetError, ConnectionAbortedError) as e:
            connection_socket.close()
            sockets = [k for k, v in client_dict.items() if v['socket'].fileno() == -1]
            for k in sockets:
                socket_open = False
                client_dict.pop(k, None)
                WARNING_PRINT(f"SOCKET {k} CLOSED")
                print(client_dict)
            sockets.clear()"""


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", SERVER_PORT))
    server_socket.listen(1)

    hostname = socket.gethostname()
    HOST_ADDRESS = socket.gethostbyname(hostname)
    print(f"Server ready for client connections at {HOST_ADDRESS}:{SERVER_PORT}")
    running = True

    while running:
        connection_socket, client_address = server_socket.accept()

        client_id = create_UID()
        while client_id in client_dict.keys():
            client_id = create_UID()
        client_dict[client_id] = {}
        client_dict[client_id]['client_name'] = "Anon-" + client_id
        client_dict[client_id]['client_address'] = client_address
        client_dict[client_id]['socket'] = connection_socket
        client_dict[client_id]['sync_mode'] = False

        print(f"Client ID '{client_id}' connected.")
        client_thread = threading.Thread(target=handle_next_client,
                                         args=(connection_socket, client_id))
        client_thread.start()

    server_socket.close()
    print("Server shutdown")


if __name__ == "__main__":
    start_server()
