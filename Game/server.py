import socket
import json

import Game.logic as logic
import Game.functions as funcs
from Game.entities import Person, Spectator

# Create a UDP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the address and port
server_address = ("localhost", 65432)
print(f"\nStarting up on {server_address[0]} port {server_address[1]}")
server_socket.bind(server_address)

while True:
    # Wait for a message
    try:
        data, address = server_socket.recvfrom(4096)
        message = data.decode("utf-8")
        m: dict = json.loads(message)

        print("Received {} bytes from {}".format(len(data), address))
        print(f"Message received: {m}")

        # m = {"type": ..., "id": ...}
        if m["type"] == "getinfo":
            data = {"type": "getinfo return"} | {i: entity.to_json_str() for i, entity in enumerate(logic.visible_to(m["id"]))}
            print(f"    Sending info: {data}")
            data = bytes(json.dumps(data), "utf-8")
            server_socket.sendto(data, address)
        # m = {"type": ..., "id": ..., "position": ..., "direction": ..., "state": ...}
        elif m["type"] == "sendinfo":
            person: Person = logic.entities[m["id"]]
            m.pop(("type", "id"))
            print(f"    Updating info: {m}")
            person.update(**m)
        # m = {"type": ..., "position": ..., "direction": ..., "state": ...}
        elif m["type"] == "join":
            m.pop("type")
            person = logic.entities.add(entity_type="Person", **funcs.json_to_dict(m))
            print(f"    Person joining. ID: {person.id}")
            return_message = {"type": "id", "value": person.id}
            return_message = json.dumps(return_message)
            data = bytes(return_message, "utf-8")
            server_socket.sendto(data, address)
        # m = {"type": ..., "id": ...}
        elif m["type"] == "leave":
            print(f"    Person/Spectator leaving. ID: {m["id"]}")
            logic.entities.remove(m["id"])
        # m = {"type": ...}
        elif m["type"] == "spectate":
            m.pop("type")
            spectator = logic.entities.add(entity_type="Spectator", **funcs.json_to_dict(m))
            print(f"    Spectator joining. ID: {spectator.id}")
            return_message = {"type": "id", "value": spectator.id}
            return_message = json.dumps(return_message)
            data = bytes(return_message, "utf-8")
            server_socket.sendto(data, address)
    except Exception as e:
        print("Error:", e)
