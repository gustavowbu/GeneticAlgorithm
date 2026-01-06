from DataTypes.Direction import Direction
from DataTypes.Vector2 import Vector2


class Entity():
    def __init__(self, id: int, position: Vector2, direction: Direction, state: str):
        self.id = id
        self.position = position
        self.direction = direction
        self.state = state

        self.speed = 5

    def tick(self):
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
