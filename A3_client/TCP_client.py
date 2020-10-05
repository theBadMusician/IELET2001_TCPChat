#!/usr/bin/python3

#################################################################################
# A Chat Client application. Used in the course IELEx2001 Computer networks, NTNU
#################################################################################

import socket
from assets.config import *
from assets.DebugTools import *

# The states that the application can be in
states = [
    "disconnected",                 # Connection to a chat server is not established
    "connected",                    # Connected to a chat server, but not authorized (not logged in)
    "authorized"                    # Connected and authorized (logged in)
]

# State variables
current_state = "disconnected"      # The current state of the system

must_run = True                     # When this variable will be set to false, the application will stop

client_socket = None                # type: socket: Use this variable to create socket connection to the chat server


def quit_application():
    """ Update the application state so that the main-loop will exit """
    # Make sure we reference the global variable here. Not the best code style,
    # but the easiest to work with without involving object-oriented code
    global must_run
    must_run = False


def send_command(command, arguments=None):
    """
    Send one command to the chat server.
    :param command: The command to send (login, sync, msg, ...(
    :param arguments: The arguments for the command as a string, or None if no arguments are needed
        (username, message text, etc)
    :return:
    """
    global client_socket
    try:
        if arguments == None:
            cmd = f"{command}\n"
        else:
            cmd = f"{command} {arguments}\n"
        client_socket.send(cmd.encode())

        # print(TextColors.OKBLUE + "\t\t\t\t  Command sent\n" + TextColors.ENDC)

    except OSError as e:
        print(TextColors.FAIL + "Error: " + e + TextColors.ENDC)


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


def get_servers_response():
    """
    Wait until a response command is received from the server
    :return: The response of the server, the whole line as a single string
    """
    # TODO Step 4: implement this function
    # Hint: reuse read_one_line (copied from the tutorial-code)
    try:
        response = read_one_line(client_socket)
        return response
    except OSError as e:
        FAIL_PRINT("Connection error: " + e)


def connect_to_server():
    # Must have these two lines, otherwise the function will not "see" the global variables that we will change here
    global client_socket
    global current_state

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_HOST, TCP_PORT))
        current_state = "connected"
        send_command("sync")                            #Sends the sync-command to the server
        if get_servers_response() == "modeok":          #Checks if sync mode was successfully enabled
            if DEBUG:
                DEBUG_PRINT("sync mode enabled.")
            OKGREEN_PRINT(f"Successfully connected to server at {SERVER_HOST}:{TCP_PORT}.")
        else:
            if DEBUG:
                DEBUG_PRINT("sync mode failed")
            FAIL_PRINT(f"Could not connect to server at {SERVER_HOST}:{TCP_PORT} in sync mode.")

    except OSError as e:
        print(TextColors.FAIL + "Connection error: " + e + TextColors.ENDC)


def disconnect_from_server():
    global client_socket
    global current_state

    try:
        client_socket.close()
        current_state = "disconnected"
        OKGREEN_PRINT("Successfully disconnected from server.")

    except OSError as e:
        FAIL_PRINT("Error: " + e)
        pass


def authorize():
    global current_state
    
    if current_state == "authorized":
        WARNING_PRINT("User already logged in.")

    else:
        username = input(TextColors.BOLD + "Enter username: " + TextColors.ENDC)
        send_command("login", username)
        response = get_servers_response()
        
        if DEBUG:
            DEBUG_PRINT(response)

        if response == "loginok":
            current_state = "authorized"
            OKGREEN_PRINT("Login successfull!")
        else:
            FAIL_PRINT(response)


def send_public_message():
    global client_socket
    msg_to_send = input(TextColors.BOLD + "Skriv inn en melding: " + TextColors.ENDC)
    send_command("msg", msg_to_send)

    response = get_servers_response()
    parsed_response = response.split(' ', 1)
    
    if DEBUG:
        DEBUG_PRINT(response)
    if parsed_response[0] == "msgok":
        OKGREEN_PRINT(f"Message sent successfully to {parsed_response[1]} users.")
    elif parsed_response[0] == "msgerr":
        FAIL_PRINT("Message wasn't sent: " + parsed_response[1])
    else:
        WARNING_PRINT("Something Happened ¯\\_(ツ)_/¯")


def send_private_message():
    global client_socket
    recv = input(TextColors.BOLD + "Hvem vil du sende til: " + TextColors.ENDC)
    msg_to_send = input(TextColors.BOLD + "Skriv inn en melding: " + TextColors.ENDC)
    send_command("privmsg", f"{recv} {msg_to_send}")

    response = get_servers_response()
    parsed_response = response.split(' ', 1)

    if DEBUG:
        DEBUG_PRINT(response)

    if parsed_response[0] == "msgok":
        OKGREEN_PRINT(f"Message sent successfully to {recv}.")
    elif parsed_response[0] == "msgerr":
        FAIL_PRINT("Message wasn't sent: " + parsed_response[1])
    else:
        WARNING_PRINT("Something Happened ¯\\_(ツ)_/¯")


def see_list_of_users():
    global client_socket
    send_command("users")

    response = get_servers_response()
    users = response.split(' ')[1:]

    if DEBUG:
        DEBUG_PRINT(response)

    UNDERLINE_PRINT(f"There are currently {len(users)} users online:")
    users.sort()
    for user in users:
        BOLD_PRINT(user)


def read_messages_in_the_inbox():
    global client_socket
    send_command("inbox")

    response = get_servers_response()
    num_lines = int(response.split(' ')[1])

    if DEBUG:
        DEBUG_PRINT(response)

    if num_lines == 0:
        OKBLUE_PRINT("You don't have any messages.")
    else:
        UNDERLINE_PRINT(f"You've got {num_lines} unread messages: \n")
        for i in range(num_lines):
            recv_msg = get_servers_response().split(' ', 2)
            msg_line = ""
            
            if recv_msg[0] == "privmsg":
                msg_line += "(Private) ".rjust(10)
            else:
                msg_line += "(Global) ".rjust(10)
            
            msg_line += f"{recv_msg[1]}: ".rjust(15)
            msg_line += recv_msg[2]

            BOLD_PRINT(msg_line)

def get_joke():
    global client_socket
    send_command("joke")

    response = get_servers_response()
    joke = response.split(' ', 1)[1]

    if DEBUG:
        DEBUG_PRINT(response)
    
    BOLD_PRINT("Server, tell me a joke! Server: ")
    OKBLUE_PRINT(joke)

"""
The list of available actions that the user can perform
Each action is a dictionary with the following fields:
description: a textual description of the action
valid_states: a list specifying in which states this action is available
function: a function to call when the user chooses this particular action. The functions must be defined before
            the definition of this variable
"""
available_actions = [
    {
        "description": "Connect to a chat server",
        "valid_states": ["disconnected"],
        "function": connect_to_server
    },
    {
        "description": "Disconnect from the server",
        "valid_states": ["connected", "authorized"],
        "function": disconnect_from_server
    },
    {
        "description": "Authorize (log in)",
        "valid_states": ["connected", "authorized"],
        "function": authorize
    },
    {
        "description": "Send a public message",
        "valid_states": ["connected", "authorized"],
        "function": send_public_message
    },
    {
        "description": "Send a private message",
        "valid_states": ["connected","authorized"],
        "function": send_private_message
    },
    {
        "description": "Read messages in the inbox",
        "valid_states": ["connected", "authorized"],
        "function": read_messages_in_the_inbox
    },
    {
        "description": "See list of users",
        "valid_states": ["connected", "authorized"],
        "function": see_list_of_users
    },
    {
        "description": "Get a joke",
        "valid_states": ["connected", "authorized"],
        "function": get_joke
    },
    {
        "description": "Quit the application",
        "valid_states": ["disconnected", "connected", "authorized"],
        "function": quit_application
    },
]


def run_chat_client():
    """ Run the chat client application loop. When this function exists, the application will stop """

    if DEBUG:
        DEBUG_PRINT("!!! CHAT CLIENT IS IN DEBUG MODE !!!")
    while must_run:
        print_menu()
        action = select_user_action()
        perform_user_action(action)
    print("Good Bye!")


def print_menu():
    """ Print the menu showing the available options """

    print("==============================================")
    print("What do you want to do now? ")
    print("==============================================")
    print("Available options:")
    i = 1
    for a in available_actions:
        if current_state in a["valid_states"]:
            # Only hint about the action if the current state allows it
            print("  %i) %s" % (i, a["description"]))
        i += 1
    print()


def select_user_action():
    """
    Ask the user to choose and action by entering the index of the action
    :return: The action as an index in available_actions array or None if the input was invalid
    """
    number_of_actions = len(available_actions)
    hint = f"{TextColors.BOLD}Enter the number of your choice (1-{number_of_actions}): {TextColors.ENDC}"
    choice = input(hint)
    print("==============================================")
    # Try to convert the input to an integer
    try:
        choice_int = int(choice)
    except ValueError:
        choice_int = -1

    if 1 <= choice_int <= number_of_actions:
        action = choice_int - 1
    else:
        action = None

    return action


def perform_user_action(action_index):
    """
    Perform the desired user action
    :param action_index: The index in available_actions array - the action to take
    :return: Desired state change as a string, None if no state change is needed
    """
    if action_index is not None:
        print()
        action = available_actions[action_index]
        if current_state in action["valid_states"]:
            function_to_run = available_actions[action_index]["function"]
            if function_to_run is not None:
                function_to_run()
            else:
                FAIL_PRINT("Internal error: NOT IMPLEMENTED (no function assigned for the action)!")
        else:
            FAIL_PRINT("This function is not allowed in the current system state (%s)" % current_state)
    else:
        WARNING_PRINT("Invalid input, please choose a valid action")
    print()
    return None

# Entrypoint for the application. In PyCharm you should see a green arrow on the left side.
# By clicking it you run the application.
if __name__ == '__main__':
    run_chat_client()