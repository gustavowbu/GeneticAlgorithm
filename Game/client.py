import json
import socket

# Create a UDP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Server address
server_address = ('localhost', 65432)
message = {"type": "join", "position": None, "direction": None, "state": None}
message = json.dumps(message)
message = bytes(message, "utf-8")
client_socket.sendto(message, server_address)

client_socket.close()
