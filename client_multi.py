from socket import *
from random import randint
from time import sleep

# from socket_liberary import read_one_line
#sd
def start_client():
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(("datakomm.work", 1301))
    need_to_run = True

    while need_to_run:
        number_to_send_1 = str(input("Velg første tall:"))
        number_to_send_2 = str(input("Velg Andre tall:"))
        number_to_send = f'{number_to_send_1}+{number_to_send_2}\n'

        print(number_to_send)
        client_socket.send(number_to_send.encode())
        server_response = client_socket.recv(100).decode()
        print("Server response:", server_response)
        sleep(1)

        if server_response == "":
            need_to_run = False

    client_socket.close()


if __name__ == '__main__':
    start_client()
