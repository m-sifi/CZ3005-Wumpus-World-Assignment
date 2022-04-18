from dataclasses import dataclass
from enum import Enum
from math import floor

class EntityType(Enum):
    NONE            = 0
    WUMPUS          = 1
    PORTAL          = 2
    COIN            = 3
    WALL            = 4

class State(Enum):
    UNKNOWN         = 0
    SAFE_VISITED    = 1
    SAFE_UNVISITED  = 2
    WUMPUS          = 3
    PORTAL          = 4
    COIN            = 5
    WALL            = 6
    UNSAFE          = 7

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

    def __repr__(self):
        status = []

        if self.confounded:
            status.append("Confounded")

        if self.stench:
            status.append("Stench")

        if self.tingle:
            status.append("Tingle")

        if self.glitter:
            status.append("Glitter")

        if self.bump:
            status.append("Bump")

        if self.scream:
            status.append("Scream")

        return f"[{'-'.join(status)}]"

@dataclass
class Agent():
    x : int = 1
    y : int = 1
    direction : Direction = Direction.NORTH
    arrow : bool = True

    percept : Percept = Percept(confounded=True)

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
        # self.status = None

        self.wumpus = None
        self.coin = None

        self.agent = None
        self.agent_start = None

        self.init()

    def init(self):
        self.data = [[ EntityType.NONE for x in range(self.width) ] for y in range(self.height)]
        # self.status = {}
        self.wumpus = None
        self.coin = None
        self.agent = Agent(1, 1, Direction.NORTH)
        self.agent_start = Agent(1, 1, Direction.NORTH)

        for x in range(self.width):
            self.data[0][x] = EntityType.WALL
            self.data[self.height - 1][x] = EntityType.WALL

        for y in range(self.height):
            self.data[y][0] = EntityType.WALL
            self.data[y][self.width - 1] = EntityType.WALL

    def percept(self, x, y):
        percept = Percept()
        current = self.data[y][x]
        neighbours = self.neighbours(x, y)

        if EntityType.PORTAL in neighbours:
            percept.tingle = True

        if EntityType.WUMPUS in neighbours:
            directions = [ (x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]

            for x, y in directions:
                if self.has_wumpus(x, y):
                    percept.stench = True
                    break

        if current == EntityType.COIN:
            percept.glitter = self.has_coin(x, y)

        # Scream?

        return percept

    def is_valid(self, x, y):
        return (0 <= x < self.width) and (0 <= y < self.height)

    def neighbours(self, x, y):
        directions = [ (x, y + 1), (x, y - 1), (x + 1, y), (x - 1, y)]
        return [ self.data[y][x] for x, y in directions if self.is_valid(x, y) ]

    def agent_forward(self):
        return self.get_forward(self.agent.x, self.agent.y, self.agent.direction)

    def get_forward(self, x, y, direction):
        if direction == Direction.NORTH:
            return x, y + 1
        elif direction == Direction.SOUTH:
            return x, y - 1
        elif direction == Direction.EAST:
            return x + 1, y
        elif direction == Direction.WEST:
            return x - 1, y

    def has_wumpus(self, x, y):
        if self.is_valid(x, y) and self.data[y][x] == EntityType.WUMPUS:
            return self.wumpus[(x, y)]

        return False

    def has_coin(self, x, y):
        if self.is_valid(x, y) and self.data[y][x] == EntityType.COIN:
            return self.coin[(x, y)]

        return False

    def reset(self):
        self.agent = Agent(self.agent_start.x, self.agent_start.y, self.agent_start.direction)
        self.status = {}
        self.wumpus = {}
        self.coin = {}

        for y in range(self.height):
            for x in range(self.width):
                if self.data[y][x] == EntityType.WUMPUS:
                    self.wumpus[(x, y)] = True

                if self.data[y][x] == EntityType.COIN:
                    self.coin[(x, y)] = True

    def to_absolute(self, x, y):
        if self.agent_start.direction == Direction.NORTH:
            return (self.agent_start.x + x, self.agent_start.y + y)
        elif self.agent_start.direction == Direction.SOUTH:
            return (self.agent_start.x - x, self.agent_start.y - y)
        elif self.agent_start.direction == Direction.EAST:
            return (self.agent_start.x + y, self.agent_start.y - x)
        elif self.agent_start.direction == Direction.WEST:
            return (self.agent_start.x - y, self.agent_start.y + x)

    def __repr__(self):
        pixels = [[ None for x in range(3 * self.width)] for y in range(3 * self.height)]

        for y in range(self.height):
            for x in range(self.width):
                symbols = [ "·" for x in range(9) ]
                percept = self.percept(x, y)

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

                    if self.has_wumpus(x, y):
                        symbols[3] = "-"
                        symbols[4] = "W"
                        symbols[5] = "-"
                    elif self.data[y][x] == EntityType.PORTAL:
                        symbols[4] = "O"
                    elif self.agent.x == x and self.agent.y == y:
                        symbols[3] = "-"
                        symbols[4] = str(self.agent)
                        symbols[5] = "-"

                __x = 3 * x
                __y = 3 * (self.height - y - 1)

                for z in range(3):
                    for w in range(3):
                        pixels[__y + z][__x + w] = symbols[z * 3 + w]

        repr = "== Absolute Map ==\n"
        for row in pixels:
            repr += " ".join(row) + "\n"

        return repr

class RelativeMap():
    def __init__(self) -> None:
        self.path   : dict = None
        self.agent  : Agent = None

        self.stench : set = None
        self.glitter : set = None
        self.tingle : set = None

        self.reset()

    def adjacent(self):
        x = self.agent.x
        y = self.agent.y

        return [ (x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    
    def reset_state(self):
        self.agent.percept.confounded = False
        self.agent.percept.bump = False
        self.agent.percept.scream = False

    def reset(self):
        percept = Percept()
        percept.confounded = True


        self.path = {(0, 0) : State.SAFE_VISITED}
        self.agent = Agent(0, 0, Direction.NORTH)

        self.stench = set()
        self.glitter = set()
        self.tingle = set()

    def get_percept(self, x, y):
        percept = Percept()

        percept.stench = True if (x, y) in self.stench else False
        percept.glitter = True if (x, y) in self.glitter else False
        percept.tingle = True if (x, y) in self.tingle else False

        return percept

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

        for coordinate, state in self.path.items():
            x, y = coordinate
            symbols = [ "·" for x in range(9) ]

            percept = self.get_percept(x, y)

            if percept.confounded:
                symbols[0] = "%"

            if percept.stench:
                symbols[1] = "="

            if percept.tingle:
                symbols[2] = "T"

            if percept.glitter:
                symbols[6] = "*"


            symbols[3] = " "
            symbols[4] = "?"
            symbols[5] = " "

            if state == State.WUMPUS:
                symbols[3] = "-"
                symbols[4] = "W"
                symbols[5] = "-"
            elif state == State.PORTAL:
                symbols[4] = "O"
            elif state == State.UNSAFE:
                symbols[3] = "-"
                symbols[4] = "U"
                symbols[5] = "-"
            elif state == State.SAFE_VISITED:
                symbols[4] = "S"
            elif state == State.SAFE_UNVISITED:
                symbols[4] = "s"

            if self.agent.x == x and self.agent.y == y:
                symbols[3] = "-"
                symbols[4] = str(self.agent)
                symbols[5] = "-"

                if self.agent.percept.bump:
                    symbols[7] = "B"

                if self.agent.percept.scream:
                    symbols[8] = "@"

            if state == State.WALL:
                symbols = [ "#" for x in range(9) ]

            px = (mid + x) * 3
            py = (size - (mid + y) - 1) * 3

            for __y in range(3):
                for __x in range(3):
                    pixels[py + __y][px + __x] = symbols[__y * 3 + __x]    

        repr = "== Relative Map ==\n"
        for row in pixels:
            repr += " ".join(row) + "\n"

        repr += f"{self.agent.percept.__repr__()}\n"

        self.reset_state()
        return repr
