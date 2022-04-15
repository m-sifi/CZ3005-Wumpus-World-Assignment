from map import *
from pyswip.easy import *
from pyswip import Prolog

class WumpusDriver():
    def __init__(self, map: Map, agent) -> None:
        self.map = map
        self.relative = None

        self.prolog = Prolog()
        self.prolog.consult(agent)

        self.reset()

    def move_forward(self):

        forward_x, forward_y = self.map.agent_forward()
        percept = self.map.percept(forward_x, forward_y)

        if self.map.data[forward_y][forward_x] == EntityType.WALL:
            percept = self.map.percept(self.map.agent.x, self.map.agent.y)
            percept.bump = True

        list(self.prolog.query(f"move(moveforward, {percept})"))

        # Update Relative Map
        self.update(percept)

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
        self.pl_current()
        self.pl_safe()
        self.pl_visited()
        self.pl_wumpus()
        self.pl_portal()
        self.pl_wall()

        cell = Cell(percept)
        self.relative.path[(self.relative.agent.x, self.relative.agent.y)] = cell


    def reset(self):
        self.relative = RelativeMap()
        reborn = Functor("reborn", 0)

        call(reborn())
        self.map.reset()

        self.update(Percept(confounded=True))

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
        safe = Functor("safe", 2)
        X = Variable()
        Y = Variable()

        q = Query(safe(X, Y))

        while q.nextSolution():
            x, y = X.value, Y.value
            print(f"Safe: {(x, y)}")
            
            cell = Cell(state=State.SAFE_UNVISITED)
            self.relative.path[(x, y)] = cell
            
        q.closeQuery()

    def pl_visited(self):
        visited = Functor("visited", 2)
        X = Variable()
        Y = Variable()

        q = Query(visited(X, Y))

        while q.nextSolution():
            x, y = X.value, Y.value
            print(f"Visited: {(x, y)}")
            
            cell = Cell(state=State.SAFE_VISITED)
            self.relative.path[(x, y)] = cell
            
        q.closeQuery()

    def pl_wumpus(self):
        wumpus = Functor("wumpus", 2)
        X = Variable()
        Y = Variable()

        q = Query(wumpus(X, Y))

        while q.nextSolution():
            x, y = X.value, Y.value
            print(f"wumpus: {(x, y)}")
            
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
            print(f"wall: {(x, y)}")

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
            print(f"portal: {(x, y)}")

            cell = Cell(state=State.PORTAL)
            self.relative.path[(X.value, Y.value)] = cell
            
        q.closeQuery()