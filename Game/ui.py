import pygame
from pygame.locals import (
    RLEACCEL,
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

from DataTypes.Direction import Direction
from DataTypes.Vector2 import Vector2
from Game.entities import Person

update = 0
entities: pygame.sprite.Group = None
all_sprites: pygame.sprite.Group = None
ADDENTITY = pygame.USEREVENT + 1

player_active: bool = False
player_id: int = None
player = None

def start():
    global update, entities, all_sprites, player_id, player

    pygame.init()

    LOGICAL_SIZE = (560, 315)
    WINDOW_SIZE = (1120, 630)
    window = pygame.display.set_mode(WINDOW_SIZE)
    canvas = pygame.Surface(LOGICAL_SIZE)

    entities = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()

    update_entities()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False

            elif event.type == QUIT:
                running = False

            elif event.type == ADDENTITY:
                if event.entity_type == "Person":
                    new_entity = Person(event.id, event.position, event.direction, event.state)
                entities.add(new_entity)
                all_sprites.add(new_entity)
                if event.id == player_id:
                    player = new_entity

        # Handling the player
        if not player is None:
            pressed_keys = pygame.key.get_pressed()
            hsp = 0
            vsp = 0
            if pressed_keys[K_UP]:
                vsp -= 1
                player.direction.update(0)
            if pressed_keys[K_RIGHT]:
                hsp += 1
                player.direction.update(1)
            if pressed_keys[K_DOWN]:
                vsp += 1
                player.direction.update(2)
            if pressed_keys[K_LEFT]:
                hsp -= 1
                player.direction.update(3)
            player.rect.move_ip(hsp, vsp)

            if hsp != 0 or vsp != 0:
                player.state = "walk"
            else:
                player.state = "idle"

        canvas.fill((155, 250, 106))

        if update <= 0:
            update_entities()
            update_file()
            update = 10
        if player_active and player_id is None:
            create_player()

        for entity in all_sprites:
            entity.tick()
            canvas.blit(entity.surf, entity.rect)

        pygame.transform.scale(canvas, WINDOW_SIZE, window)
        pygame.display.flip()

        update -= 1
        clock = pygame.time.Clock()
        clock.tick(60)

    # Update the file when the game is finished
    player.kill()
    update_file()

# Function not used. Code rewritten in update_entities() for the sake of performance.
def get_entities_from_file():
    with open("Game/entities.txt") as file:
        file = file.readlines()

    new_entities = []
    for entity in file:
        entity = entity[:-1]
        properties = entity.split("; ")
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
            entity = Person(**dictionary)
        else:
            raise ValueError("'entity_type' must be 'Person', ")

        new_entities.append(entity)

    return new_entities

def update_entities():
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
        file.write(new_content)
