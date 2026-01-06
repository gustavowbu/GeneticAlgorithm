import math
from typing import Self


class Vector2():
    def __init__(self, x: float = 0, y: float = 0):
        self.x = float(x)
        self.y = float(y)

    def from_str(self, string: str) -> Self:
        """ returns a new Vector2 from a string in the format 'Vector2(x, y)' """

        result = Vector2()
        string = string[8:-1].split(", ")
        result.x = float(string[0])
        result.y = float(string[1])
        return result

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Vector2({self.x}, {self.y})"

    def __getitem__(self, key: int) -> float:
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        raise KeyError(key)

    def __len__(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def __eq__(self, other) -> bool:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            return self.x == other and self.y == other
        return self.x == other.x and self.y == other.y

    def __ne__(self, other) -> bool:
        return not (self == other)

    def __gt__(self, other) -> bool:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            return len(self) > other
        return len(self) > len(other)

    def __lt__(self, other) -> bool:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            return len(self) < other
        return len(self) < len(other)

    def __ge__(self, other) -> bool:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            return len(self) >= other
        return len(self) >= len(other)

    def __le__(self, other) -> bool:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            return len(self) <= other
        return len(self) <= len(other)

    def gt(self, other: Self) -> bool:
        other = to_Vector2(other)
        return self.x > other.x and self.y > other.y

    def lt(self, other: Self) -> bool:
        other = to_Vector2(other)
        return self.x < other.x and self.y < other.y

    def ge(self, other: Self) -> bool:
        other = to_Vector2(other)
        return self.x >= other.x and self.y >= other.y

    def le(self, other: Self) -> bool:
        other = to_Vector2(other)
        return self.x <= other.x and self.y <= other.y

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def neg_x(self):
        return Vector2(-self.x, self.y)

    def neg_y(self):
        return Vector2(self.x, self.y)

    def __add__(self, other) -> Self:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            return Vector2(self.x + other, self.y + other)
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other) -> Self:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            return Vector2(self.x - other, self.y - other)
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other) -> Self:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            return Vector2(self.x * other, self.y * other)
        return Vector2(self.x * other.x, self.y * other.y)

    def dotproduct(self, other) -> float:
        other = to_Vector2(other)
        return self.x * other.x + self.y * other.y

    def __truediv__(self, other) -> Self:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            return Vector2(self.x / other, self.y / other)
        return Vector2(self.x / other.x, self.y / other.y)

    def __floordiv__(self, other) -> Self:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            return Vector2(self.x // other, self.y // other)
        return Vector2(self.x // other.x, self.y // other.y)

    def __mod__(self, other) -> Self:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            return Vector2(self.x % other, self.y % other)
        return Vector2(self.x % other.x, self.y % other.y)

    def __mod__(self, other) -> Self:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            return Vector2(self.x % other, self.y % other)
        return Vector2(self.x % other.x, self.y % other.y)

    def __divmod__(self, other) -> tuple[Self, Self]:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            x = divmod(self.x, other)
            y = divmod(self.y, other)
        else:
            x = divmod(self.x, other.x)
            y = divmod(self.y, other.y)
        return Vector2(x[0], y[0]), Vector2(x[1], y[1])

    def __pow__(self, other) -> Self:
        other = to_Vector2(other) if not isinstance(other, (int, float)) else other
        if isinstance(other, (int, float)):
            return Vector2(self.x ** other, self.y ** other)
        return Vector2(self.x ** other.x, self.y ** other.y)

    def to_list(self) -> list[float]:
        return [self.x, self.y]

    def to_list_int(self) -> list[int]:
        return [int(self.x), int(self.y)]

    def to_tuple(self) -> tuple[float]:
        return tuple(self.to_list())

    def to_tuple_int(self) -> tuple[int]:
        return tuple(self.to_list_int())

def to_Vector2(object) -> Vector2:
    if isinstance(object, (list, tuple)):
        if len(object) == 2:
            return Vector2(object[0], object[1])
    elif isinstance(object, Vector2):
        return object
    raise ValueError(f"'{object}' not convertable to Vector2")
