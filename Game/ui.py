import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.locals import (
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

from DataTypes.Vector2 import Vector2
from DataTypes.Direction import Direction
from Game.EntityList import EntityList
from Game.entities_ui import EntitySprite, HumanSprite, SpectatorSprite

import client

# Variables
entities = EntityList()
all_sprites: pygame.sprite.Group = pygame.sprite.Group()

# Functions
def update_entities():
    game_entities = client.getinfo()
    for entity in game_entities:
        # New entity
        if not entity.id in entities:
            entity_sprite = entity.to_Sprite()
            entities.append(entity_sprite)
            all_sprites.add(entity_sprite)
        # Existing entity
        else:
            entity_sprite: EntitySprite = entities[entity.id]

            # Update information
            entity_sprite.position = entity.position
            entity_sprite.direction = entity.direction
            entity_sprite.state = entity.state

        # Adjusting position relative to the camera
        entity_sprite.position = entity_sprite.position + Vector2(LOGICAL_SIZE[0], LOGICAL_SIZE[1]) / 2 - camera_position

    # Dead entities
    for entity_sprite in entities:
        if not entity_sprite.id in game_entities:
            entities.remove(entity_sprite.id)

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
    update_entities()
    clock = pygame.time.Clock()
    clock.tick(60)

client.leave_server()
