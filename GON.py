import json
from typing import Any

from DataTypes.Direction import Direction
from DataTypes.Vector2 import Vector2
from Game.EntityList import EntityList
from Game.entities import Entity, Human, Spectator

class Gon(): # Game Object Notation
    def __init__(self):
        pass

    def dumps(self, value: dict | list) -> str:
        return json.dumps(self._parse_iterator(value))

    def _parse_iterator(self, value: dict | list) -> dict | list:
        if isinstance(value, dict):
            for key in value:
                if isinstance(value[key], (int, float, bool, str)):
                    pass
                elif isinstance(value[key], (list, dict)):
                    value[key] = Gon()._parse_iterator(value[key])
                else:
                    if hasattr(value[key], "to_GON"):
                        value[key] = value[key].to_GON(self)
                    else:
                        value[key] = str(value[key])
        elif isinstance(value, list):
            for i in range(len(value)):
                if isinstance(value[i], (int, float, bool, str)):
                    pass
                elif isinstance(value[i], (list, dict)):
                    value[i] = Gon()._parse_iterator(value[i])
                else:
                    if hasattr(value[i], "to_GON"):
                        value[i] = value[i].to_GON()
                    else:
                        value[i] = str(value[i])
        else:
            raise TypeError("'value' must be dict or list")
        return value

    def loads(self, string: str) -> dict | list:
        value = json.loads(string)
        new_value = value.copy()

        # Parse dictionary keys
        if isinstance(value, dict):
            new_value = {}
            value: dict[str, Any]
            for key in value:
                new_value[self._parse_value(key)] = value[key]

        # Parse values
        if isinstance(new_value, dict):
            for key in new_value:
                new_value[key] = self._parse_value(new_value[key])

        elif isinstance(new_value, list):
            for i in range(len(new_value)):
                new_value[i] = self._parse_value(new_value[i])

        return new_value

    def _parse_value(self, value):
        if isinstance(value, (dict, list)):
            return self.loads(self.dumps(value))

        elif isinstance(value, str):
            accepted_datatypes = ["Vector2", "Direction", "EntityList", "Entity", "Human", "Spectator"]
            value_is_adt = False
            for datatype in accepted_datatypes:
                if value.startswith(datatype):
                    value_is_adt = True
                    value_type = datatype
                    break
            if value_is_adt:
                brackets = value.find("(")
                value = value[brackets + 1:]

                kwargs = {}
                key = ""
                vvalue = ""
                state = "key"
                brackets = 1
                for i in range(len(value)):
                    c = value[i]
                    if c == "(" or c == "[":
                        brackets += 1
                    if c == ")" or c == "]":
                        brackets -= 1
                        if brackets == 0:
                            kwargs[key] = self._parse_value(vvalue)
                            key = ""
                            vvalue = ""
                            break

                    if state == "key":
                        if c == "=":
                            state = "value"
                            continue
                        if c != " " or key != "":
                            key += c
                    elif state == "value":
                        if c == "," and brackets == 1:
                            kwargs[key] = self._parse_value(vvalue)
                            key = ""
                            vvalue = ""
                            state = "key"
                            continue
                        vvalue += c

                if value_type == "Vector2":
                    value = Vector2(**kwargs)
                elif value_type == "Direction":
                    value = Direction(**kwargs)
                elif value_type == "EntityList":
                    value = EntityList(**kwargs)
                elif value_type == "Entity":
                    value = Entity(**kwargs)
                elif value_type == "Human":
                    value = Human(**kwargs)
                elif value_type == "Spectator":
                    value = Spectator(**kwargs)

            else:
                try:
                    return int(value)
                except:
                    pass
                try:
                    return float(value)
                except:
                    pass
                if value in ("true", "false"):
                    return value == "true"
                if (value.startswith("[") and value.endswith("]")) or (value.startswith("{") and value.endswith("}")):
                    return self.loads(value)

        return value
