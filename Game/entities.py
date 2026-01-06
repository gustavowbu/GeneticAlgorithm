from typing import Self
from DataTypes.Direction import Direction
from DataTypes.Vector2 import Vector2


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

class Human(Entity):
    def __init__(self, id: int, position: Vector2, direction: Direction, state: str):
        super().__init__(id, position, direction, state)

class Spectator(Entity):
    def __init__(self, id: int, position: Vector2, direction: Direction, state: str):
        super().__init__(id, position, direction, state)
