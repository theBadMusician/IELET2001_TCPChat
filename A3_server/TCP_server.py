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

print(joke_list)

def create_UID():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

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

def handle_next_client(connection_socket, client_id):
    command = 'x'
    while command != "":
        command = read_one_line(connection_socket)
        print(f"Client ID '{client_id}': {command}")
        if command == "ping":
            response = "PONG\n"
        elif command == "sync":
            response = "modeok\n"
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
        while client_id in client_dict:
            client_id = create_UID()
        client_dict[client_id] = {}
        client_dict[client_id]['client_name'] = "Anonymous" + client_dict[client_id]
        print(client_dict)

        print(f"Client ID '{client_id}' connected.")
        client_thread = threading.Thread(target=handle_next_client,
                                         args=(connection_socket, client_id))
        client_thread.start()

    welcome_socket.close()
    print("Server shutdown")


if __name__ == "__main__":
    start_server()
