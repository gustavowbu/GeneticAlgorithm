import pygame
from pygame.locals import RLEACCEL

from DataTypes.Direction import Direction
from DataTypes.Vector2 import Vector2


class Entity(pygame.sprite.Sprite):
    animation_fps = 60

    def __init__(self, id: int, position: Vector2, direction: Direction, state: str):
        # Game logic
        self.id = id
        self.position = position
        self.direction = direction
        self.state = state

        # UI logic
        super(Entity, self).__init__()

        ## Default animation
        self.animations = {}
        for state in ["idle", "walk", "run"]:
            filepath = f"Game/assets/Female/Unarmed/With_shadow/Unarmed_{state.capitalize()}_with_shadow.png"
            animation_names = [f"{state}_{direction}" for direction in ["down", "left", "right", "up"]] # This order is important because it is the order in which the animations appear in the images
            self.animations |= load_animations(filepath, 64, 64, animation_names)

        self.animation_index = 0
        self.animation_name = self.state + "_" + self.direction.name
        self.surf: pygame.Surface = self.animations[self.animation_name][0]
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.rect.center = position.to_tuple()

    def tick(self):
        self.animation_name = self.state + "_" + self.direction.name
        if self.state == "idle":
            self.animation_fps = 10
        else:
            self.animation_fps = 20

        ticks_per_frame = 60 // self.animation_fps
        num_frames = len(self.animations[self.animation_name])

        self.animation_index += 1
        self.animation_index = self.animation_index % (num_frames * ticks_per_frame)

        animation_index = self.animation_index // ticks_per_frame
        self.surf = self.animations[self.animation_name][animation_index]
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"id: {self.id}; entity_type: {self.__class__.__name__}; position: {self.position}; direction: {self.direction.number}; state: {self.state}"

class Person(Entity):
    animation_fps = 20

    def __init__(self, id: int, position: Vector2, direction: Direction, state: str):
        super().__init__(id, position, direction, state)

        self.animations = {}
        for state in ["idle", "walk", "run"]:
            filepath = f"Game/assets/Female/Unarmed/With_shadow/Unarmed_{state.capitalize()}_with_shadow.png"
            animation_names = [f"{state}_{direction}" for direction in ["down", "left", "right", "up"]] # This order is important because it is the order in which the animations appear in the images
            self.animations |= load_animations(filepath, 64, 64, animation_names)

        self.surf = self.animations[self.animation_name][0]
        self.surf.set_colorkey((255, 255, 255), RLEACCEL)
        self.rect = self.surf.get_rect()
        self.rect.center = position.to_tuple()


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
