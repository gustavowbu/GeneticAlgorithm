import json
from typing import Self

from DataTypes.Vector2 import Vector2
from DataTypes.Direction import Direction
from Game.entities import Entity, Human, Spectator

class EntityList():
    default_position = Vector2(0, 0)
    entity_id = 0

    iter_index = 0

    def __init__(self, entities: list[Entity] = None):
        self.entities = entities if not entities is None else []

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self.entities)

    def to_json_str(self) -> str:
        return json.dumps({i: entity.to_dict() for i, entity in enumerate(self.entities)})

    def __bytes__(self) -> bytes:
        return bytes(self.to_json_str())

    def add(self, entity_type: str, position: Vector2 = None, direction: int = None, state: str = None):
        """ Adds an entity and returns it. """

        if position is None:
            position = self.default_position
        if direction is None:
            direction = Direction("n")
        if state is None:
            state = "idle"

        if entity_type == "Human":
            entity = Human(self.entity_id, position, direction, state)
        elif entity_type == "Spectator":
            entity = Spectator(self.entity_id, position, direction, state)
        else:
            raise ValueError("'entity_type' must be 'Human' or 'Spectator'")
        self.entity_id += 1

        self.entities.append(entity)

        return entity

    def append(self, entity: Entity):
        self.entities.append(entity)

    def remove(self, id: int):
        """ Removes the entity with the given ID and returns it. """

        for i in range(len(self.entities)):
            if self.entities[i].id == id:
                return self.entities.pop(i)
        raise IndexError(f"No entity with id '{id}'")

    def __getitem__(self, id: int) -> Entity:
        for i in range(len(self.entities)):
            if self.entities[i].id == id:
                return self.entities[i]
        raise IndexError(f"No entity with id '{id}'")

    def find(self, id: int) -> Entity:
        for i in range(len(self.entities)):
            if self.entities[i].id == id:
                return self.entities[i]
        return -1

    def __contains__(self, id: int) -> bool:
        for entity in self.entities:
            if entity.id == id:
                return True
        return False

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> Entity:
        if self.iter_index < len(self.entities):
            entity = self.entities[self.iter_index]
            self.iter_index += 1
            return entity
        self.iter_index = 0
        raise StopIteration
