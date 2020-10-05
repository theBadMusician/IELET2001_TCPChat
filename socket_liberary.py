def read_one_line(client_socket):
    newline_recieved = False
    message = ""
    while not newline_recieved:
        character = client_socket.recv(1).decode()
        if character == '\n':
            newline_recieved = True
        elif character == '\r':
            pass
        else:
            message += character
    return message






