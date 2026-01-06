from DataTypes.Vector2 import Vector2
from Game.EntityList import EntityList


world_max = Vector2(800, 600) # from -800, -600 to 800, 600
camera_size = Vector2(560, 315) # from -280, -157.5 to 280, 157.5 or from 0, 0 to 560, 315
entities = EntityList()

def visible_to(id: int) -> EntityList:
    viewing_entity = entities[id]
    p = viewing_entity.position
    c = camera_size / 2
    camera = (p + c.neg_y(), p + c, p + c.neg_x(), p - c)

    visible = EntityList()
    for entity in entities:
        if entity.is_in_area(camera):
            visible.append(entity)
    return visible
