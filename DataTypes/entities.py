from typing import Self
from DataTypes.Direction import Direction
from DataTypes.Vector2 import Vector2
from Game.entities_ui import EntitySprite, HumanSprite, SpectatorSprite


class Entity():
    def __init__(self, id: int, position: Vector2, direction: Direction, state: str):
        self.id = id
        self.position = position
        self.direction = Direction(direction)
        self.state = state

        self.speed = 5

    def from_str(self, string: str) -> Self:
        """ returns a new Entity from a string in the format 'Entity(id, position, direction, state)' """

        result = type(self)()
        string = string[7:-1].split(", ")
        result.id = int(string[0])
        result.position = Vector2().from_str(string[1])
        result.direction = Direction().from_str(string[2])
        result.state = string[3]
        return result

    def tick(self, globals: dict):
        if self.state == "walk":
            north = "n" in self.direction.name
            east = "e" in self.direction.name
            south = "s" in self.direction.name
            west = "w" in self.direction.name

            hsp = east - west
            vsp = south - north

            if hsp and vsp:
                hsp /= 1.414213562
                vsp /= 1.414213562

            self.position += (hsp, vsp)

            world_max: Vector2 = globals["world_max"]

            if self.position.x > world_max.x:
                self.position.x = world_max.x
            elif self.position.x < -world_max.x:
                self.position.x = -world_max.x
            if self.position.y > world_max.y:
                self.position.y = world_max.y
            elif self.position.y < -world_max.y:
                self.position.y = -world_max.y

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, position={self.position}, direction={self.direction}, state={self.state})"

    def to_Sprite(self) -> EntitySprite:
        return EntitySprite(self.id, self.position, self.direction, self.state)

    """ def update(self, position: Vector2, direction: Direction, state: str):
        self.position = position
        self.direction = direction
        self.state = state

    def get_four_corners(self) -> tuple[Vector2, Vector2, Vector2, Vector2]:
        tr = self.position + Vector2(self.width, -self.height) / 2
        br = self.position + Vector2(self.width, self.height) / 2
        bl = self.position - Vector2(self.width, -self.height) / 2
        tl = self.position - Vector2(self.width, self.height) / 2
        return tr, br, bl, tl

    def is_in_area(self, area: tuple[Vector2, Vector2, Vector2, Vector2]) -> bool:
        tr, br, bl, tl = self.get_four_corners()
        area_tr, area_br, area_bl, area_tl = area

        # Flipping the top right and bottom left corners in the x axis
        # so that it's easier to check
        bl = bl.neg_x()
        area_tr = area_tr.neg_x()
        tr = tr.neg_x()
        area_bl = area_bl.neg_x()
        return (br.gt(area_tl) and tl.lt(area_br)) or (bl.gt(area_tr) and tr.lt(area_bl)) """

    def copy(self) -> Self:
        return type(self)(id=self.id, position=self.position, direction=self.direction, state=self.state)

class Human(Entity):
    def __init__(self, id: int, position: Vector2, direction: Direction, state: str):
        super().__init__(id, position, direction, state)

    def to_Sprite(self) -> HumanSprite:
        return HumanSprite(self.id, self.position, self.direction, self.state)

class Spectator(Entity):
    def __init__(self, id: int, position: Vector2, direction: Direction, state: str):
        super().__init__(id, position, direction, state)

    def to_Sprite(self) -> SpectatorSprite:
        return SpectatorSprite(self.id, self.position, self.direction, self.state)
