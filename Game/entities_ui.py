import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.locals import RLEACCEL

from DataTypes.Direction import Direction
from DataTypes.Vector2 import Vector2


class EntitySprite(pygame.sprite.Sprite):
    animation_fps = 60
    width = 0
    height = 0

    def __init__(self, id: int, position: Vector2 = None, direction: Direction = None, state: str = None):
        # Game logic
        self.id = id
        self.position = position if not position is None else Vector2()
        self.direction = direction if not direction is None else Direction("up")
        self.state = state if not state is None else "idle"

        # UI logic
        super(EntitySprite, self).__init__()

        ## Default animation
        self.animations = {}
        for state in ["idle", "walk", "run"]:
            filepath = f"Game/assets/Female/Unarmed/With_shadow/Unarmed_{state.capitalize()}_with_shadow.png"
            animation_names = [f"{state}_{direction}" for direction in ["s", "w", "e", "n"]] # This order is important because it is the order in which the animations appear in the sprites
            self.animations |= load_animations(filepath, 64, 64, animation_names)

        self.animation_index = 0
        self.animation_name = self.state + "_" + self.direction.get_4_direction_name()
        self.surf: pygame.Surface = self.animations[self.animation_name][0]
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)

        self.rect = self.surf.get_rect()
        self.rect.center = self.position.to_tuple()

    def tick(self):
        self.animation_name = self.state + "_" + self.direction.get_4_direction_name()
        if self.state == "idle":
            self.animation_fps = 10
        else:
            self.animation_fps = 15

        ticks_per_frame = 60 // self.animation_fps
        num_frames = len(self.animations[self.animation_name])

        self.animation_index += 1
        self.animation_index = self.animation_index % (num_frames * ticks_per_frame)

        animation_index = self.animation_index // ticks_per_frame
        self.surf = self.animations[self.animation_name][animation_index]
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)

        self.rect.center = self.position.to_tuple()

    def move(self, x: float = 0, y: float = 0):
        self.rect.move_ip(x, y)

    def move_to(self, x: float, y: float):
        self.rect.center = (x, y)

class HumanSprite(EntitySprite):
    animation_fps = 20
    width = 15
    height = 25

    def __init__(self, id: int, position: Vector2 = None, direction: Direction = None, state: str = None):
        super().__init__(id, position, direction, state)

        # UI logic
        ## Default animation
        self.animations = {}
        for state in ["idle", "walk", "run"]:
            filepath = f"Game/assets/Female/Unarmed/With_shadow/Unarmed_{state.capitalize()}_with_shadow.png"
            animation_names = [f"{state}_{direction}" for direction in ["s", "w", "e", "n"]] # This order is important because it is the order in which the animations appear in the sprites
            self.animations |= load_animations(filepath, 64, 64, animation_names)

        self.animation_index = 0
        self.animation_name = self.state + "_" + self.direction.get_4_direction_name()
        self.surf: pygame.Surface = self.animations[self.animation_name][0]
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)

        self.rect = self.surf.get_rect()
        self.rect.center = self.position.to_tuple()

class SpectatorSprite(EntitySprite):
    def __init__(self, id: int, position: Vector2 = None, direction: Direction = None, state: str = None):
        super().__init__(id, position, direction, state)

        # UI logic
        self.surf = pygame.Surface((16, 16))
        for key1 in self.animations:
            self.animations[key1] = {0: pygame.Surface((16, 16), pygame.SRCALPHA)}


def load_animations(filepath: str, frame_width, frame_height, animation_names):
    sprite_sheet = pygame.image.load(filepath).convert_alpha()
    NUM_FRAMES = sprite_sheet.get_width() // frame_width
    NUM_ANIMATIONS = sprite_sheet.get_height() // frame_height

    sprites: dict[str, list[pygame.Surface]] = {}
    for i_animation in range(NUM_ANIMATIONS):
        key = animation_names[i_animation]
        sprites[key] = []
        for i_frame in range(NUM_FRAMES):
            frame = sprite_sheet.subsurface(pygame.Rect(i_frame * frame_width, i_animation * frame_height, frame_width, frame_height))
            sprites[key].append(frame)
    return sprites
