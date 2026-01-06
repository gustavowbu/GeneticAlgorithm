from DataTypes.Vector2 import Vector2
from DataTypes.Direction import Direction
from GON import Gon

value = {1: {"a": 3, 4.5: "c"}, "c": [5, 6.7, 8], False: 9, 10: [Vector2(), Direction(0)]}
print(value)
string = Gon().dumps(value)
print(string)
value = Gon().loads(string)
print(value)

print()

value = [{"a": 3, 4.5: "c"}, [5, 6.7, 8], False, 9, Vector2(), Direction(0)]
print(value)
string = Gon().dumps(value)
print(string)
value = Gon().loads(string)
print(value)
