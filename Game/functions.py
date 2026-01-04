from typing import Any
import json

from DataTypes.Vector2 import Vector2
from DataTypes.Direction import Direction

def json_to_dict(json_dict: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(json_dict, str):
        json_dict: dict[str, Any] = json.loads(json_dict)

    for key in json_dict:
        item = json_dict[key]

        if isinstance(item, str):
            if item.startswith("Vector2(") and item.endswith(")"):
                item = item[8:-1].split(", ")
                item = Vector2(float(item[0]), float(item[1]))
        if key == "direction":
            if isinstance(item, int):
                item = Direction(int(item))
            elif item is None:
                item = Direction("up")
            else:
                raise TypeError("'direction' must be an instance of int")
        json_dict[key] = item

    return json_dict
