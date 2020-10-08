import argparse

# Enable for DEBUG printouts
DEBUG = 1


#TCP_PORT = 1300                     # TCP port used for communication
#SERVER_HOST = "datakomm.work"       # Set this to either hostname (domain) or IP address of the chat server

TCP_PORT = 80                     # TCP port used for communication
SERVER_HOST = "192.168.0.225"       # Set this to either hostname (domain) or IP address of the chat server


parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug",
                    help="Set True for debug printouts. Default: False",
                    type=bool, metavar='')
parser.add_argument("-p", "--port",
                    help="Port number to use for connection. Default: 1300",
                    type=int, metavar='')
parser.add_argument("-a", "--address",
                    help="Host server IP address or domain name address. Default: 'datakomm.work'",
                    metavar='')
args = parser.parse_args()

if args.debug:
    DEBUG = args.debug
    print(f"Debug printouts are set to: {DEBUG}")

if args.port:
    TCP_PORT = args.port
    print(f"Port used: {TCP_PORT}")

if args.address:
    SERVER_HOST = args.address
    print(f"Host server address (domain or IP): {SERVER_HOST}")