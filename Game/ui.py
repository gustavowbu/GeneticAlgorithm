import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)
import json
import socket

from DataTypes.Vector2 import Vector2
from DataTypes.Direction import Direction
from Game.EntityList import EntityList
from Game.entities import Entity, Human, Spectator

import client

# Variables
entities = EntityList()
all_sprites: pygame.sprite.Group = pygame.sprite.Group()

# Functions
client_socket = None
server_address = ('localhost', 65432)
spectator_id: int = None
def join_server():
    global client_socket, spectator_id
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    message = {"type": "spectate", "position": str(Vector2(0, 0)), "direction": None, "state": None}
    message = json.dumps(message)
    data = bytes(message, "utf-8")

    # Sending spectate message
    client_socket.sendto(data, server_address)

    # Waiting for a response
    data, server = client_socket.recvfrom(4096)
    message = data.decode("utf-8")
    m: dict = json.loads(message)

    if m["type"] == "id":
        spectator_id = m["value"]
    else:
        raise TypeError(f"Invalid message type '{message["type"]}'. Expected 'id'")

# Function not used. Code rewritten in update_entities() for the sake of performance.
def update_entities():
    # Sending getinfo message
    message = {"type": "getinfo", "id": spectator_id}
    message = json.dumps(message)
    message = bytes(message, "utf-8")
    client_socket.sendto(message, server_address)

    # Waiting for a response
    data, server = client_socket.recvfrom(4096)
    message = data.decode("utf-8")
    m: dict = json.loads(message)

    if m["type"] == "getinfo return":
        m.pop("type")
        for key in m.keys():
            new_entity = funcs.json_to_dict(m[key])

            # Adjusting position relative to the camera
            new_entity["position"] = new_entity["position"] + Vector2(LOGICAL_SIZE[0], LOGICAL_SIZE[1]) / 2 - camera_position

            if new_entity["id"] in entities:
                entity = entities[new_entity["id"]]
                entity.position = new_entity["position"]
                entity.direction = new_entity["direction"]
                entity.state = new_entity["state"]
            else:
                if new_entity["entity_type"] == "Human":
                    new_entity.pop("entity_type")
                    new_entity = Human(**new_entity)
                elif new_entity["entity_type"] == "Spectator":
                    continue #TODO: Implement
                else:
                    raise TypeError("'entity_type' must be 'Human'")
                new_entity.init_ui()
                entities.append(new_entity)
                print(new_entity)
                all_sprites.add(new_entity)
    else:
        raise TypeError(f"Invalid message type '{message["type"]}'. Expected 'id'")

# Init pygame
pygame.init()

# Window variables
LOGICAL_SIZE = (560, 315)
WINDOW_SIZE = (1120, 630)
camera_position = Vector2(0, 0)
window = pygame.display.set_mode(WINDOW_SIZE)
canvas = pygame.Surface(LOGICAL_SIZE)

# Connect to server
client.spectate_server()

running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False

        elif event.type == QUIT:
            running = False

    # Fill with background
    canvas.fill((155, 250, 106))

    # Display and tick sprites
    # update_entities()
    for sprite in all_sprites:
        canvas.blit(sprite.surf, sprite.rect)
        sprite.tick()

    # Display
    pygame.transform.scale(canvas, WINDOW_SIZE, window)
    pygame.display.flip()

    # Tick
    clock = pygame.time.Clock()
    clock.tick(60)

client.leave_server()
