#!/usr/bin/python3

#################################################################################
# Gruppe 24: J. Dyrskog, E. Fagerbakke, M. Gaddour, V. Moland, B. Visockis      #
# Øving A3 09.10.20 IELET2001 (Datakommunikasjon) NTNU, Trondheim               #
#################################################################################

# This server code was written to follow the specs layed out in the A3
# Chat Protocol document and be compatible with the precompiled helping client
# and our own standard CLI client.

from assets.DebugTools import *
import socket
import threading
import random
import string

# Set to run with debugging printouts..
DEBUG = 0

# Port used by server
SERVER_PORT = 80

# client_dict stores necessary info about clients i.e.
# UID, name (username), address, sync/async mode, socket object
client_dict = {}

# Implemented commands. This list is used in case of client-side 'help' command.
cmd_list = ['sync', 'async',
            'login',
            'msg', 'privmsg',
            'inbox', 'users',
            'joke', 'help']

# Loads jokes from jokes.txt file to joke_list variable. All jokes end in '\n' char.
joke_list = []
with open("assets/jokes.txt", "r") as jokes:
    for line in jokes:
        joke_list.append(line)


def create_UID():
    """
    Creates 8 char long Unique Identifier (UID) in alphanumerical format. Chars used: 0-9, a-z, A-Z.
    :return: (str) Alphanumeric ID of length 8
    """
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def read_one_line(sock):
    """
    Read one line of text from a socket. In case recv is unreadable it catches connection error.
    :param sock: (socket.socket) The socket to read from.
    :return: (str) message, (int) -1 (in case of dead socket/unreadable msg)
    """
    newline_received = False
    message = ""
    while not newline_received:
        try:
            character = sock.recv(1).decode()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
            return -1
        if character == '\n':
            newline_received = True
        elif character == '\r':
            pass
        else:
            message += character
    return message


def check_connections(client_id):
    """
    Performs connection check on all sockets in client_dict dictionary,
    except for the one which called this function.
    Should be called whenever caller socket is impacted/can impact other sockets, i.e. login, messaging, checking users.
    :param client_id: (str) Caller socket ID.
    :return: None
    """
    for dict_client_id in tuple(client_dict):
        if client_id != dict_client_id:
            try:
                # Sends 'ping' to known sockets. Uses char '\r' which passed by read_one_line function.
                client_dict[dict_client_id]['socket'].send("\r".encode())
                if DEBUG:
                    WARNING_PRINT("SENT CHECK TO " + dict_client_id)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
                # In case 'ping' returns a ConnectionError, close the socket.
                client_dict[dict_client_id]['socket'].close()
    if DEBUG:
        print("<<<<================>")


def cleanup_disconnections():
    """
    Cleans up closed sockets.
    Checks client_dict for sockets with fileno == -1 which means dc'ed socket and deletes it from client_dict.
    NOTE: socket handling and closing itself is performed in check_connections and handle_client functions.
    :return: None
    """
    # Creates a list with closed sockets. List is used to avoid runtime errors in regard to changing dict size.
    dead_sockets = [k for k, v in client_dict.items() if v['socket'].fileno() == -1]
    for k in dead_sockets:
        # Deletes closed keys from client_dict.
        client_dict.pop(k, None)
        WARNING_PRINT(f"SOCKET {k} CLOSED")
        if DEBUG:
            print(client_dict)


def handle_login_req(client_id, login_req_parsed):
    """
    Handles login requests from client.
    :param client_id: (str) Caller socket ID.
    :param login_req_parsed: (list) Parsed login request - split command e.g. ['login', 'username1']
    :return: (str) Response to send to client. Either 'loginerr' or 'loginok'.
    """
    username = login_req_parsed[1]

    # Error handling
    if ' ' in username:
        return "loginerr incorrect username format\n"
    elif any(username in name['client_name'] for name in client_dict.values()):
        return "loginerr username already in use\n"

    # Set username to client_id in client_dict and return response.
    else:
        client_dict[client_id]['client_name'] = username
        return "loginok\n"


def handle_msg_req(client_id, msg_req_parsed):
    """
    Handles global/public message requests.
    :param client_id: (str) Caller socket ID.
    :param msg_req_parsed: (list) Parsed message request using split method. E.g. ['msg', 'Hey, how is it going?']
    :return: (str) Response to send to caller socket.
    """
    msg = msg_req_parsed[1]

    # Response to be broadcasted to other sockets.
    response_string = f"msg {client_dict[client_id]['client_name']} {msg}\n"
    try:
        for dict_client_id in client_dict.keys():
            # Hop over if it's the caller socket.
            if client_id == dict_client_id:
                continue
            # If client is in 'sync mode', store in the client_dict instead of sending it.
            elif client_dict[dict_client_id]['sync_mode']:
                client_dict[dict_client_id]['inbox'].append(response_string)
            # If client is in 'async mode', send the message.
            else:
                client_dict[dict_client_id]['socket'].send(response_string.encode())
        # Response for the caller socket.
        return f"msgok {len(client_dict) - 1}\n"
    # In case anything goes wrong. Not the best solution.
    except Exception:
        return "msgerror Something happened ¯\\_(ツ)_/¯\n"


def handle_privmsg_req(client_id, msg_req_parsed):
    """
    Handles private message requests.
    :param client_id: (str) Caller socket ID.
    :param msg_req_parsed: (list) Parsed message request using split method. E.g. ['msg', 'username', 'Hey, how is it going?']
    :return: (str) Response for the caller socket.
    """
    recipient_msg = msg_req_parsed[1].split(' ', 1)
    recipient = recipient_msg[0]

    # Check if user is in client_dict database
    try:
        recipient_id = [k for k, v in client_dict.items() if recipient in v['client_name']][0]
    except IndexError:
        return "msgerr incorrect recipient\n"

    # Response for the recipient socket.
    msg = recipient_msg[1]
    response_string = f"privmsg {client_dict[client_id]['client_name']} {msg}\n"

    # Check if sender socket/user is anonymous.
    if client_dict[client_id]['client_name'] == "Anon-" + str(client_id):
        return "msgerr unauthorized\n"

    # Check if recipient exists in client_dict.
    elif not any(recipient in name['client_name'] for name in client_dict.values()):
        return "msgerr incorrect recipient\n"

    # Check if recipient is anonymous user.
    elif recipient == "Anon-" + str(recipient_id):
        return "msgerr incorrect recipient\n"

    # Check if recipient is in 'sync mode'. If it is, store the message in the database.
    elif client_dict[recipient_id]['sync_mode']:
        try:
            client_dict[recipient_id]['inbox'].append(response_string)
            # Response for the caller socket.
            return f"msgok 1\n"
        except Exception:
            return "msgerror Something happened ¯\\_(ツ)_/¯\n"

    # If recipient is in 'async mode', send the message.
    else:
        try:
            client_dict[recipient_id]['socket'].send(response_string.encode())
            return f"msgok 1\n"
        except Exception:
            return "msgerror Something happened ¯\\_(ツ)_/¯\n"


def handle_client(connection_socket, client_id):
    """
    Main client-socket-loop function. Handles all requests and connections.
    Refers requests to appropriate functions.
    :param connection_socket: (socket.socket) Caller socket object.
    :param client_id: (str) Caller socket ID.
    :return: None
    """
    # True as long as socket isn't dead/closed.
    socket_open = True

    # Socket call loop.
    while socket_open:

        # Receives buffer from the socket.
        command = read_one_line(connection_socket)

        # Try to parse the command with split method, if it has arguments.
        try:
            command_parsed = command.split(' ', 1)
        except AttributeError:
            pass
        print(f"Client ID '{client_id}': {command}")

        # If read_one_line can't read from socket, 'command' variable returns -1.
        # It means the socket is most likely dead/closed/unresponsive.
        # In that case loop is broken, socket connection is closed from server side, and its local info is flushed.
        if command == -1:
            socket_open = False
            connection_socket.close()
            cleanup_disconnections()
            continue

        # Sets socket in 'sync mode', where it needs to give explicit commands to communicate with server.
        # Creates an 'inbox' for the socket in the database. In case client reinstates 'sync mode', 'inbox' is flushed.
        elif command == "sync":
            client_dict[client_id]['sync_mode'] = True
            client_dict[client_id]['inbox'] = []
            # Response for the caller socket.
            response = "modeok\n"

        # Sets socket in 'async mode', client then needs to be able to receive w/out command reqs or it'll lose data.
        elif command == "async":
            client_dict[client_id]['sync_mode'] = False
            # 'Inbox' is flushed.
            client_dict[client_id]['inbox'] = []
            response = "modeok\n"

        # Saves a non "Anon-xxxxxxxx" name for the user in the database. Returns an appropriate response to the socket.
        elif command_parsed[0] == "login":
            # Checks if known connections are still alive.
            check_connections(client_id)
            response = handle_login_req(client_id, command_parsed)

        # Broadcasts a public message to sockets/inboxes.
        elif command_parsed[0] == "msg":
            check_connections(client_id)
            response = handle_msg_req(client_id, command_parsed)

        # Sends a private message to specified recipient.
        elif command_parsed[0] == "privmsg":
            check_connections(client_id)
            response = handle_privmsg_req(client_id, command_parsed)

        # Checks inbox for the user, and returns received messages. Flushes contents after checking.
        elif command == "inbox":
            client_inbox = client_dict[client_id]['inbox']
            inbox_contents = ''.join([str(elem) for elem in client_inbox])
            response = "inbox " + str(len(client_inbox)) + "\n" + str(inbox_contents)
            client_dict[client_id]['inbox'] = []

        # Checks online users and returns their usernames.
        elif command_parsed[0] == "users":
            # TODO: Fix the bug of users not updating at the moment of calling. Maybe use setInterval solution instead.
            check_connections(client_id)
            client_names_list = [v['client_name'] for k, v in client_dict.items()]
            client_names = ' '.join([str(elem) for elem in client_names_list])
            response = "users " + client_names + "\n"

        # Sends back a joke stored in joke_list variable.
        elif command == "joke":
            joke = joke_list[random.randint(0, len(joke_list) - 1)]
            response = "joke " + joke

        # Gives a list of names of supported functions to the client.
        elif command == "help":
            cmds = ' '.join([str(elem) for elem in cmd_list])
            response = "supported " + cmds + "\n"

        # Commands that aren't here, are not supported and return 'cmderr' error.
        else:
            response = "cmderr command not supported"
        connection_socket.send(response.encode())


def main_server():
    """
    Server setup and main loop function. Sets up server socket mode, port, max concurrent connection calls.
    Sets up new client connections and assigns them to threads.
    TODO: Setup shutdown method other than KeyboardInterrupt.
    :return: None
    """

    # Server socket setup.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", SERVER_PORT))
    server_socket.listen(1)

    # Print server local IP address and port.
    hostname = socket.gethostname()
    HOST_ADDRESS = socket.gethostbyname(hostname)
    print(f"Server ready for client connections at {HOST_ADDRESS}:{SERVER_PORT}")

    # Socket welcoming loop. Sets up new connections and assigns threads.
    running = True
    while running:
        # Gets socket object and address.
        connection_socket, client_address = server_socket.accept()

        # Creates and assigns new UID. Checks for dublicates and handles them.
        client_id = create_UID()
        while client_id in client_dict.keys():
            client_id = create_UID()

        # Creates new key-value in client_dict database. Uses the UID as key. Other info is stored in nested dict.
        client_dict[client_id] = {}

        # Assigns anonymous "Anon-xxxxxxxx" name first.
        client_dict[client_id]['client_name'] = "Anon-" + client_id

        # Saves sockets address (IP address and port).
        client_dict[client_id]['client_address'] = client_address

        # Saves the socket object.
        client_dict[client_id]['socket'] = connection_socket

        # Assigns socket the 'async' mode at first. If socket sends 'sync' command it is reassigned to 'sync' status.
        client_dict[client_id]['sync_mode'] = False

        # Assigns the socket to a new thread.
        client_thread = threading.Thread(target=handle_client,
                                         args=(connection_socket, client_id))
        client_thread.start()
        print(f"Client ID '{client_id}' connected.")

    # Currently not accessible.
    server_socket.close()
    print("Server shutdown")


if __name__ == "__main__":
    main_server()
