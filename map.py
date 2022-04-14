from dataclasses import dataclass
from enum import Enum
from math import floor

class EntityType(Enum):
    NONE            = 0
    WUMPUS          = 1
    PORTAL          = 2
    COIN            = 3
    WALL            = 4

class Direction(Enum):
    NORTH   = 0
    EAST    = 1
    SOUTH   = 2
    WEST    = 3

@dataclass
class Percept():
    confounded : bool = False
    stench : bool = False
    tingle : bool = False
    glitter : bool = False
    bump : bool = False
    scream : bool = False

    def __str__(self):
        convert = lambda x: "on" if x else "off"
        return f"[{convert(self.confounded)}, {convert(self.stench)}, {convert(self.tingle)}, {convert(self.glitter)}, {convert(self.bump)}, {convert(self.scream)}]" 
        

@dataclass
class Agent():
    x : int = 1
    y : int = 1
    direction : Direction = Direction.NORTH
    arrow : bool = True

    def __str__(self):
        if self.direction == Direction.NORTH:
            return "∧"
        elif self.direction == Direction.SOUTH:
            return "∨"
        if self.direction == Direction.EAST:
            return ">"
        elif self.direction == Direction.WEST:
            return "<"

class Map():
    def __init__(self):
        self.width  = 7
        self.height = 6

        self.data = None
        self.agent = None

        self.init()

    def init(self):
        self.data = [[ EntityType.NONE for x in range(self.width) ] for y in range(self.height)]
        self.agent = Agent(1, 1, Direction.NORTH)

        for x in range(self.width):
            self.data[0][x] = EntityType.WALL
            self.data[self.height - 1][x] = EntityType.WALL

        for y in range(self.height):
            self.data[y][0] = EntityType.WALL
            self.data[y][self.width - 1] = EntityType.WALL

    def get_percept(self, x, y):
        percept = Percept()
        current = self.data[y][x]
        neighbours = self.neighbours(x, y)

        if EntityType.PORTAL in neighbours:
            percept.tingle = True

        if EntityType.WUMPUS in neighbours:
            percept.stench = True

        if current == EntityType.COIN:
            percept.glitter = True

        return percept

    def is_valid(self, x, y):
        return (0 <= x < self.width) and (0 <= y < self.height)

    def neighbours(self, x, y):
        directions = [ (x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]
        return [ self.data[y][x] for x, y in directions if self.is_valid(x, y) ]

    def __repr__(self):
        pixels = [[ None for x in range(3 * self.width)] for y in range(3 * self.height)]

        for y in range(self.height):
            for x in range(self.width):
                symbols = [ "·" for x in range(9) ]
                percept = self.get_percept(x, y)

                if self.data[y][x] == EntityType.WALL:
                    symbols = [ "#" for x in range(9) ]
                else:
                    if percept.confounded:
                        symbols[0] = "%"

                    if percept.stench:
                        symbols[1] = "="

                    if percept.tingle:
                        symbols[2] = "T"

                    if percept.glitter:
                        symbols[6] = "*"

                    # Absolute Map will never show bump but we keep this here so I can reference later :)
                    # if percept.bump:
                    #     symbols[7] = "B"

                    # Absolute Map will never show scream but we keep this here so I can reference later :)
                    # if percept.scream:
                    #     symbols[8] = "@"

                    symbols[3] = " "
                    symbols[4] = "?"
                    symbols[5] = " "

                    if self.data[y][x] == EntityType.WUMPUS:
                        symbols[3] = "-"
                        symbols[4] = "W"
                        symbols[5] = "-"
                    elif self.agent.x == x and self.agent.y == y:
                        symbols[3] = "-"
                        symbols[4] = str(self.agent)
                        symbols[5] = "-"

                __x = 3 * x
                __y = 3 * (self.height - y - 1)

                for z in range(3):
                    for w in range(3):
                        pixels[__y + z][__x + w] = symbols[z * 3 + w]

        repr = ""
        for row in pixels:
            repr += " ".join(row) + "\n"

        return repr

class RelativeMap():
    def __init__(self) -> None:
        self.path   : dict = None
        self.agent  : Agent = None

        self.reset()
    
    def reset_state(self):
        for coordinate, percept in self.path.items():
            # clear if has state BUMP or SCREAM or CONFOUNDED
            percept.confounded = False
            percept.bump = False
            percept.scream = False

            self.path[coordinate] = percept

    def reset(self):
        percept = Percept()
        percept.confounded = True

        self.path = {(0, 0) : percept}
        self.agent = Agent(0, 0, Direction.NORTH)

    def __size(self):
        Xs = []
        Ys = []
        
        for x, y in self.path.keys():
            Xs.append(x)
            Ys.append(y)
            
        width = ((max(Xs) + 1) * 2) + 1
        height = ((max(Ys) + 1) * 2) + 1

        return width if width > height else height

    def __repr__(self):
        size = self.__size()
        pixels = [[ " " for x in range(3 * size)] for y in range(3 * size)]

        mid = floor(size / 2)

        for coordinate, percept in self.path.items():
            x, y = coordinate
            symbols = [ "·" for x in range(9) ]

            if percept.confounded:
                symbols[0] = "%"

            if percept.stench:
                symbols[1] = "="

            if percept.tingle:
                symbols[2] = "T"

            if percept.glitter:
                symbols[6] = "*"

            # Absolute Map will never show bump but we keep this here so I can reference later :)
            # if percept.bump:
            #     symbols[7] = "B"

            # Absolute Map will never show scream but we keep this here so I can reference later :)
            # if percept.scream:
            #     symbols[8] = "@"


            symbols[3] = " "
            symbols[4] = "?"
            symbols[5] = " "
            # if self.data[y][x] == EntityType.WUMPUS:
            #     symbols[3] = "-"
            #     symbols[4] = "W"
            #     symbols[5] = "-"

            if self.agent.x == x and self.agent.y == y:
                symbols[3] = "-"
                symbols[4] = str(self.agent)
                symbols[5] = "-"

            px = (mid + x) * 3
            py = (size - (mid + y) - 1) * 3

            for __y in range(3):
                for __x in range(3):
                    pixels[py + __y][px + __x] = symbols[__y * 3 + __x]    

        repr = ""
        for row in pixels:
            repr += " ".join(row) + "\n"

        self.reset_state()
        return repr
