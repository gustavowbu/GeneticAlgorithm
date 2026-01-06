import threading
import time

from DataTypes.Vector2 import Vector2
from Game.EntityList import EntityList


world_max = Vector2(800, 600) # from -800, -600 to 800, 600
camera_size = Vector2(560, 315) # from -280, -157.5 to 280, 157.5 or from 0, 0 to 560, 315
entities = EntityList()
loaded_entities = EntityList()
globals = {"world_max": world_max, "camera_size": camera_size}

""" def visible_to(id: int) -> EntityList:
    viewing_entity = entities[id]
    p = viewing_entity.position
    c = camera_size / 2
    camera = (p + c.neg_y(), p + c, p + c.neg_x(), p - c)

    visible = EntityList()
    for entity in entities:
        if entity.is_in_area(camera):
            visible.append(entity)
    return visible """

tps = 2

def tick():
    for entity in loaded_entities:
        entity.tick(globals)

stop_event = threading.Event()
def tick_thread(tps: int):
    current_time = time.time()
    spt = 1 / tps
    while not stop_event.is_set():
        time_ellapsed = time.time() - current_time
        if time_ellapsed > spt:
            current_time = time.time()
            tick()

thread = threading.Thread(target=tick_thread, args=(tps, ))
thread.start()
