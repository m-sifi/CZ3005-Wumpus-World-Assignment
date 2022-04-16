from random import randint
from map import *
from pyswip.easy import *
from pyswip import Prolog

class WumpusDriver():
    def __init__(self, map: Map, agent) -> None:
        self.map = map
        self.relative = None

        self.prolog = Prolog()
        self.prolog.consult(agent)

        self.restart()

    def move_forward(self):
        forward_x, forward_y = self.map.agent_forward()
        percept = self.map.percept(forward_x, forward_y)

        if self.map.data[forward_y][forward_x] == EntityType.WALL:
            percept = self.map.percept(self.map.agent.x, self.map.agent.y)
            percept.bump = True

        if self.map.data[forward_y][forward_x] == EntityType.PORTAL:
            self.reset()
            percept = self.map.percept(self.map.agent.x, self.map.agent.y)
            percept.confounded = True

        list(self.prolog.query(f"move(moveforward, {percept})"))

        # Update Relative Map
        self.update(percept)

    def shoot(self):
        percept = self.map.percept(self.map.agent.x, self.map.agent.y)

        if self.map.agent.arrow:
            x = self.map.agent.x
            y = self.map.agent.y
            direction = self.map.agent.direction

            while self.map.is_valid(x, y):
                if self.map.data[y][x] == EntityType.WUMPUS:
                    if self.map.status[(x, y)] == True:
                        self.map.status[(x, y)] = False
                        percept.scream = True

                x, y = self.map.get_forward(x, y, direction)

        list(self.prolog.query(f"move(shoot, {percept})"))
        # Update Relative Map
        self.update(percept)

    def pickup_coin(self):
        percept = self.map.percept(self.map.agent.x, self.map.agent.y)

        if percept.glitter:
            for y in range(self.map.height):
                for x in range(self.map.height):
                    if self.map.data[y][x] == EntityType.COIN:
                        if self.map.status[(x, y)] == True:
                            percept.glitter = False
                            self.map.status[(x, y)] = False

        list(self.prolog.query(f"move(pickup, {percept})"))
        # Update Relative Map
        self.update(percept)

    def explore(self):
        permutations = list(map(lambda x: x["L"], list(self.prolog.query(f"explore(L)"))))
        selected = permutations.pop(0)

        for action in selected:
            if action == "moveforward":
                self.move_forward()
            elif action == "turnleft":
                self.turn_left()
            elif action == "turnright":
                self.turn_right()

    def turn_left(self):
        percept = self.map.percept(self.map.agent.x, self.map.agent.y)
        list(self.prolog.query(f"move(turnleft, {percept})"))

        # Update Relative Map
        self.update(percept)

    def turn_right(self):
        percept = self.map.percept(self.map.agent.x, self.map.agent.y)
        list(self.prolog.query(f"move(turnright, {percept})"))

        # Update Relative Map
        self.update(percept)

    def update(self, percept):
        # self.plf_visited()
        self.pl_wumpus()
        self.pl_portal()
        self.pl_wall()
        self.pl_current()
        self.pl_safe()

        # self.pl_listing("visited(X, Y)")
        # self.pl_listing("confundus(X, Y)")
        # self.pl_listing("wumpus(X, Y)")

        cell = Cell(percept)
        self.relative.path[(self.relative.agent.x, self.relative.agent.y)] = cell

        self.map.agent.arrow = bool(list(self.prolog.query("hasarrow")))


    def restart(self):
        self.relative = RelativeMap()
        reborn = Functor("reborn", 0)

        call(reborn())
        self.map.reset()

        self.update(Percept(confounded=True))

    def reset(self):
        self.relative = RelativeMap()
        x = 0
        y = 0
        direction = Direction(randint(0, 3))

        while(self.map.data[y][x] != EntityType.NONE):
            x = randint(1, self.map.width - 2)
            y = randint(1, self.map.height - 2)

        self.map.agent_start.x = x
        self.map.agent_start.y = y
        self.map.agent_start.direction = direction

        self.map.reset()

    def pl_current(self):
        current = Functor("current", 3)
        X = Variable()
        Y = Variable()
        D = Variable()

        q = Query(current(X, Y, D))
        q.nextSolution()

        self.relative.agent.x = X.value
        self.relative.agent.y = Y.value

        direction = str(D.value) \
                        .strip()

        if direction== "rnorth":
            # print("rnorth")
            self.relative.agent.direction = Direction.NORTH
        elif direction == "reast":
            # print("reast")
            self.relative.agent.direction = Direction.EAST
        elif direction == "rsouth":
            # print("rsouth")
            self.relative.agent.direction = Direction.SOUTH
        elif direction == "rwest":
            # print("rwest")
            self.relative.agent.direction = Direction.WEST

        # Convert Relative -> Absolute
        x, y = self.map.to_absolute(self.relative.agent.x, self.relative.agent.y)
        self.map.agent.x = x
        self.map.agent.y = y

        if self.map.agent_start.direction == Direction.NORTH:
            self.map.agent.direction = Direction((self.relative.agent.direction.value + 0) % 4)
        elif self.map.agent_start.direction == Direction.EAST:
            self.map.agent.direction = Direction((self.relative.agent.direction.value + 1) % 4)
        elif self.map.agent_start.direction == Direction.SOUTH:
            self.map.agent.direction = Direction((self.relative.agent.direction.value + 2) % 4)
        elif self.map.agent_start.direction == Direction.WEST:
            self.map.agent.direction = Direction((self.relative.agent.direction.value + 3) % 4)

        # print(self.map.agent.x, self.map.agent.y, self.map.agent.direction)
        # print(self.relative.agent.x, self.relative.agent.y, self.relative.agent.direction)

        q.closeQuery()

    def pl_safe(self):
        adjacent = self.relative.adjacent()

        for x, y in adjacent:
            if self.safe(x, y):
                cell = Cell(state=State.SAFE_UNVISITED)
                self.relative.path[(x, y)] = cell

        for coordinate, cell in self.relative.path.items():
            x, y = coordinate

            if self.visited(x, y):
                cell.state = State.SAFE_VISITED

    # def pl_unsafe(self):
 
    def pl_wumpus(self):
        wumpus = Functor("wumpus", 2)
        X = Variable()
        Y = Variable()

        q = Query(wumpus(X, Y))

        while q.nextSolution():
            x, y = X.value, Y.value
            
            cell = Cell(state=State.WUMPUS)
            self.relative.path[(x, y)] = cell
            
        q.closeQuery()

    def pl_wall(self):
        wall = Functor("wall", 2)
        X = Variable()
        Y = Variable()

        q = Query(wall(X, Y))

        while q.nextSolution():
            x, y = X.value, Y.value

            cell = Cell(state=State.WALL)
            self.relative.path[(x, y)] = cell
            
        q.closeQuery()

    def pl_portal(self):
        confundus = Functor("confundus", 2)
        X = Variable()
        Y = Variable()

        q = Query(confundus(X, Y))

        while q.nextSolution():
            x, y = X.value, Y.value

            cell = Cell(state=State.PORTAL)
            self.relative.path[(X.value, Y.value)] = cell
            
        q.closeQuery()

    def safe(self, x, y):
        return bool(list(self.prolog.query(f"safe({x}, {y})")))

    def visited(self, x, y):
        return bool(list(self.prolog.query(f"visited({x}, {y})")))

    def pl_listing(self, query):
        print(f"{query}: {list(self.prolog.query(query))}")