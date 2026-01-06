import socket

from GON import Gon

# Create a UDP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server address
server_address = ('localhost', 65432)

# Variables
gon = Gon()
id = None

# Functions
def _send_message(message: dict):
    message_str = gon.dumps(message)
    data = bytes(message_str, "utf-8")
    client_socket.sendto(data, server_address)

def _receive_message() -> dict:
    data = client_socket.recv(4096)
    message: dict = gon.loads(data.decode("utf-8"))
    return message

def sign_up_to_server():
    """ Joins the server as a human and returns the id. """

    global id

    message = {"type": "sign up"}
    _send_message(message)
    message = _receive_message()
    if message["type"] == "id":
        id = message["value"]
        print(f"Signed up to server with id {id}")
        return message["value"]
    elif message["type"] == "error":
        return message["description"]

def sign_in_to_server(id: int):
    """ Joins the server with the given id. """

    message = {"type": "sign in", "id": id}
    _send_message(message)

def spectate_server() -> int:
    """ Joins the server as a spectator and returns the id. """

    global id

    message = {"type": "spectate"}
    _send_message(message)
    message = _receive_message()
    if message["type"] == "id":
        id = message["value"]
        print(f"Spectating server with id {id}")
        return message["value"]
    elif message["type"] == "error":
        return message["description"]

def leave_server():
    message = {"type": "leave", "id": id}
    _send_message(message)
    client_socket.close()
    print("Left server.")

def getinfo():
    """ Gets entity info from the server. """

    message = {"type": "getinfo"}
    _send_message(message)
    message = _receive_message()
    if message["type"] == "game info update":
        return message["entities"]
    elif message["type"] == "error":
        return message["description"]
