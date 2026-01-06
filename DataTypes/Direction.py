from typing import Self


class Direction():
    number: int
    name: str

    def __init__(self, direction: str | int):
        self.update(direction)

    def from_str(self, string: str) -> Self:
        """ returns a new Direction from a string in the format 'Direction(direction)' """

        string = string[10:-1]
        try:
            string = int(string)
        except:
            pass
        return Direction(string)

    def update(self, direction: str | int):
        if isinstance(direction, str):
            direction = direction.lower()
            if not direction in ("n", "ne", "e", "se", "s", "sw", "w", "nw"):
                raise ValueError("'direction' must be int or 'n', 'ne', 'e', 'se', 's', 'sw', 'w' or 'nw'")
            self.name = direction
            self.number = {"n": 0, "ne": 1, "e": 2, "se": 3, "s": 4, "sw": 5, "w": 6, "nw": 7}[direction]
        elif isinstance(direction, int):
            direction = direction % 4
            self.number = direction
            self.name = {0: "n", 1: "ne", 2: "e", 3: "se", 4: "s", 5: "sw", 6: "w", 7: "nw"}[direction]

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return f"Direction({self.name})"

    def __int__(self) -> int:
        return self.number

    def __float__(self) -> float:
        return float(int(self))

    def __eq__(self, other: int | str) -> bool:
        if not isinstance(other, (int, str)):
            raise ValueError("'other' must be int or str")
        return self.number == other or self.name == other

    def __ne__(self, other: int | str) -> bool:
        return not self == other

    def __add__(self, other: int) -> Self:
        if not isinstance(other, int):
            raise ValueError("'other' must be int")
        return Direction(self.number + other)

    def __sub__(self, other: int) -> Self:
        if not isinstance(other, int):
            raise ValueError("'other' must be int")
        return Direction(self.number - other)

    def __mul__(self, other: int) -> Self:
        if not isinstance(other, int):
            raise ValueError("'other' must be int")
        return Direction(self.number * other)

    def __truediv__(self, other: int) -> Self:
        if not isinstance(other, int):
            raise ValueError("'other' must be int")
        return Direction(self.number // other)

    def __mod__(self, other: int) -> Self:
        if not isinstance(other, int):
            raise ValueError("'other' must be int")
        return Direction(self.number % other)

    def __divmod__(self, other: int) -> tuple[Self, Self]:
        if not isinstance(other, int):
            raise ValueError("'other' must be int")
        direction = divmod(self.number, other)
        return Direction(direction[0]), Direction(direction[1])

    def __pow__(self, other: int) -> Self:
        if not isinstance(other, int):
            raise ValueError("'other' must be int")
        return Direction(self.number ** other)

    def __floordiv__(self, other: int):
        if not isinstance(other, int):
            raise ValueError("'other' must be int")
        return Direction(self.number // other)
