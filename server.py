import socket

import Game.logic as logic
from GON import Gon

gon = Gon()

# Create a UDP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the address and port
server_address = ("localhost", 65432)
print(f"\nStarting up server on address {server_address[0]} port {server_address[1]}")
server_socket.bind(server_address)

# Variables
joined_ids = []

# Functions
def send_message(message: dict, address):
    message_str = gon.dumps(message)
    data = bytes(message_str, "utf-8")
    server_socket.sendto(data, address)

def kick_id(id: int):
    for i in range(len(joined_ids)):
        if joined_ids[i] == id:
            joined_ids.pop(i)
            break

while True:
    # Wait for a message
    try:
        data, address = server_socket.recvfrom(4096)
        message = data.decode("utf-8")
        m: dict = gon.loads(message)

        print("\nReceived {} bytes from {}".format(len(data), address))
        print(f"Message received: {m}")

        # m = {"type": ...}
        if m["type"] == "sign up":
            m.pop("type")
            human = logic.entities.add(entity_type="Human")
            logic.load_entity(human.id)
            print(f"    Human joining.")
            print(f"    Sending message with id: {human.id}")
            send_message({"type": "id", "value": human.id}, address)
        # m = {"type": ..., "id": ...}
        elif m["type"] == "sign in":
            # TODO
            """ m.pop("type")
            person = logic.entities.add(entity_type="Person", **m)
            print(f"    Person joining. ID: {person.id}")
            return_message = {"type": "id", "value": person.id}
            return_message = json.dumps(return_message)
            data = bytes(return_message, "utf-8")
            server_socket.sendto(data, address) """
        # m = {"type": ...}
        elif m["type"] == "spectate":
            m.pop("type")
            spectator = logic.entities.add(entity_type="Spectator")
            logic.load_entity(spectator.id)
            print(f"    Spectator joining.")
            print(f"    Sending message with id: {spectator.id}")
            send_message({"type": "id", "value": spectator.id}, address)
        # m = {"type": ..., "id": ...}
        elif m["type"] == "leave":
            id = m["id"]
            logic.unload_entity(id)
            print(f"    Human/Spectator leaving. ID: {id}")
            kick_id(id)
            print(f"    Sending goodbye message.")
            send_message({"type": "text", "info": "You left the server. We will miss you."}, address)
        # m = {"type": ...}
        elif m["type"] == "getinfo":
            message = {"type": "game info update"} | {"entities": logic.loaded_entities.copy()}
            send_message(message, address)
            print(f"    Sending info: {message}")
        # m = {"type": ..., "id": ..., "position": ..., "direction": ..., "state": ...}
        elif m["type"] == "sendinfo":
            # TODO
            """ person: Person = logic.entities[m["id"]]
            m.pop(("type", "id"))
            print(f"    Updating info: {m}")
            person.update(**m) """
    except Exception as e:
        print("Error:", e)
