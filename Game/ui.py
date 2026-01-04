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
from Game.entities import Entity, Person
import Game.functions as funcs

# Variables
update = 10

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
                if new_entity["entity_type"] == "Person":
                    new_entity.pop("entity_type")
                    new_entity = Person(**new_entity)
                elif new_entity["entity_type"] == "Spectator":
                    continue #TODO: Implement
                else:
                    raise TypeError("'entity_type' must be 'Person'")
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
join_server()

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
    update_entities()
    for sprite in all_sprites:
        canvas.blit(sprite.surf, sprite.rect)
        sprite.tick()

    # Display
    pygame.transform.scale(canvas, WINDOW_SIZE, window)
    pygame.display.flip()

    # Tick
    clock = pygame.time.Clock()
    clock.tick(60)
    update -= 1

""" def update_entities():
    global entities, ADDENTITY, player_id
    entities_alive = [False for i in range(len(entities))]


    with open("Game/entities.txt") as file:
        file = file.readlines()

    new_entities = []
    for new_entity in file:
        new_entity = new_entity[:-1]
        properties = new_entity.split("; ")
        dictionary = {}
        for property in properties:
            key, value = property.split(": ")
            if value.isdecimal():
                value = int(value)
            elif value.startswith("Vector2"):
                x, y = value[8:-1].split(", ")
                value = Vector2(float(x), float(y))
            if key == "direction":
                value = Direction(value)
            dictionary[key] = value

        entity_type = dictionary["entity_type"]
        dictionary.pop("entity_type")
        if entity_type == "Person":
            new_entity = Person(**dictionary)
        else:
            raise ValueError("'entity_type' must be 'Person', ")

        new_entities.append(new_entity)

        match = False
        for index, entity in enumerate(entities):
            if entity.id == new_entity.id:
                entities_alive[index] = True
                match = True
                break
        if match: # Updating existing entities
            if new_entity.id != player_id: # Don't update the player
                entity.position = new_entity.position
                entity.direction = new_entity.direction
                entity.state = new_entity.state
        else: # Adding new entities
            pygame.event.post(
                pygame.event.Event(
                    ADDENTITY,
                    id=new_entity.id,
                    entity_type=new_entity.__class__.__name__,
                    position=new_entity.position,
                    direction=new_entity.direction,
                    state=new_entity.state
                )
            )

    for index, entity in enumerate(entities): # Removing missing entities
        if not entities_alive[index]:
            entity.kill()

def get_entity_by_id(id: int):
    global entities

    for entity in entities:
        if entity.id == id:
            return entity

def activate_player():
    global player_active
    player_active = True

def create_player():
    global entities, player_id, ADDENTITY

    # Getting highest id
    player_id = 0
    for entity in entities:
        if entity.id > player_id:
            player_id = entity.id
    player_id += 1

    pygame.event.post(
        pygame.event.Event(
            ADDENTITY,
            id=player_id,
            entity_type="Person",
            position=Vector2(280, 157.5),
            direction=Direction(2),
            state="idle"
        )
    )

    with open("Game/entities.txt", "a") as file:
        file.write(f"id: {player_id}; entity_type: Person; position: Vector2(280, 157.5); direction: 2; state: idle\n")

def update_file():
    new_content = ""
    for entity in entities:
        new_content += str(entity) + "\n"

    with open("Game/entities.txt", "w") as file:
        file.write(new_content) """
