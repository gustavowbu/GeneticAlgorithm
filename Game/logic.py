from DataTypes.Vector2 import Vector2
from DataTypes.Direction import Direction
from Game.entities import Entity, Person


world = Vector2(800, 600)
entities: list[Entity] = []
last_id = 0

def add_entity(entity_type: str, position: Vector2 = None, direction: int = None):
    global entities, last_id

    if position is None:
        position = world / 2
    if direction is None:
        direction = Direction("up")

    if entity_type == "Person":
        entity = Person(last_id, position, direction)
    else:
        raise ValueError("'entity_type' must be 'Person', ")
    last_id += 1

    entities.append(entity)

def move_entity(id: int, position: Vector2):
    entity = gebi(id)
    entity.position = position

def get_entity_by_id(id: int) -> Entity:
    for i in range(len(entities)):
        if entities[i].id == id:
            return entities[i]
    raise IndexError(f"No entity with id '{id}'")

def gebi(id: int) -> Entity:
    return get_entity_by_id(id)
