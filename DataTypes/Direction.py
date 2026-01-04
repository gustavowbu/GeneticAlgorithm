from typing import Self


class Direction():
    number: int
    name: str

    def __init__(self, direction: str | int):
        self.update(direction)

    def update(self, direction: str | int):
        if isinstance(direction, str):
            direction = direction.lower()
            if not direction in ("up", "right", "down", "left"):
                raise ValueError("'direction' must be int or 'up', 'right', 'down' or 'left'")
            self.name = direction
            self.number = {"up": 0, "right": 1, "down": 2, "left": 3}[direction]
        elif isinstance(direction, int):
            direction = direction % 4
            self.number = direction
            self.name = {0: "up", 1: "right", 2: "down", 3: "left"}[direction]

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return self.name

    def __int__(self) -> int:
        return self.number

    def __float__(self) -> float:
        return float(int(self))

    def __add__(self, other: int) -> Self:
        if isinstance(other, int):
            return Direction(self.number + other)
        raise ValueError("'other' must be int")

    def __sub__(self, other: int) -> Self:
        if isinstance(other, int):
            return Direction(self.number - other)
        raise ValueError("'other' must be int")

    def __mul__(self, other: int) -> Self:
        if isinstance(other, int):
            return Direction(self.number * other)
        raise ValueError("'other' must be int")

    def __truediv__(self, other: int) -> Self:
        if isinstance(other, int):
            return Direction(self.number // other)
        raise ValueError("'other' must be int")

    def __mod__(self, other: int) -> Self:
        if isinstance(other, int):
            return Direction(self.number % other)
        raise ValueError("'other' must be int")

    def __divmod__(self, other: int) -> tuple[Self, Self]:
        if isinstance(other, int):
            direction = divmod(self.number, other)
            return Direction(direction[0]), Direction(direction[1])
        raise ValueError("'other' must be int")

    def __pow__(self, other: int) -> Self:
        if isinstance(other, int):
            return Direction(self.number ** other)
        raise ValueError("'other' must be int")

    def __floordiv__(self, other: int):
        if isinstance(other, int):
            return Direction(self.number // other)
        raise ValueError("'other' must be int")
