import json
from typing import Any

from DataTypes.Direction import Direction
from DataTypes.Vector2 import Vector2

class Gon(): # Game Object Notation
    def __init__(self):
        pass

    def dumps(self, value: dict | list) -> str:
        return json.dumps(self.parse_iterator(value))

    def parse_iterator(self, value: dict | list) -> dict | list:
        if isinstance(value, dict):
            for key in value:
                if isinstance(value[key], (int, float, bool, str)):
                    pass
                elif isinstance(value[key], (list, dict)):
                    value[key] = Gon().parse_iterator(value[key])
                else:
                    value[key] = str(value[key])
        elif isinstance(value, list):
            for i in range(len(value)):
                if isinstance(value[i], (int, float, bool, str)):
                    pass
                elif isinstance(value[i], (list, dict)):
                    value[i] = Gon().parse_iterator(value[i])
                else:
                    value[i] = str(value[i])
        else:
            raise TypeError("'value' must be dict or list")
        return value

    def loads(self, string: str) -> dict:
        value = json.loads(string)
        new_value = value

        # Correct dictionary keys
        if isinstance(value, dict):
            new_value = {}
            value: dict[str, Any]
            for key in value:
                try:
                    new_value[int(key)] = value[key]
                    continue
                except:
                    pass
                try:
                    new_value[float(key)] = value[key]
                    continue
                except:
                    pass
                if key in ("true", "false"):
                    new_value[key == "true"] = value[key]
                    continue
                new_value[key] = value[key]

        # Correct items
        if isinstance(new_value, dict):
            for key in new_value:
                new_value[key] = self.correct_item(new_value[key])

        elif isinstance(new_value, list):
            for i in range(len(new_value)):
                new_value[i] = self.correct_item(new_value[i])

        return new_value

    def correct_item(self, item):
        if isinstance(item, (dict, list)):
            return self.loads(self.dumps(item))

        elif isinstance(item, str):
            if item.startswith("Vector2"):
                return Vector2().from_str(item)
            if item.startswith("Direction"):
                return Direction(0).from_str(item)
