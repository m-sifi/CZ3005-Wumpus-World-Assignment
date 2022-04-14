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
        percept = self.map.percept(self.map.agent.x, self.map.agent.y)

        forward_x, forward_y = self.map.agent_forward()

        if self.map.data[forward_y][forward_x] == EntityType.WALL:
            percept.bump = True

        list(self.prolog.query(f"move(moveforward, {percept})"))

        # Update Relative Map
        self.update(percept)

    def update(self, percept):
        self.pl_current()
        self.pl_safe()

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

        if D.value == "rnorth":
            self.relative.agent.direction = Direction.NORTH
        elif D.value == "reast":
            self.relative.agent.direction = Direction.EAST
        elif D.value == "rsouth":
            self.relative.agent.direction = Direction.SOUTH
        elif D.value == "rwest":
            self.relative.agent.direction = Direction.WEST

        # Convert Relative -> Absolute
        x, y = self.map.to_absolute(self.relative.agent.x, self.relative.agent.y)
        self.map.agent.x = x
        self.map.agent.y = y

        q.closeQuery()

    def pl_safe(self):
        safe = Functor("safe", 2)
        X = Variable()
        Y = Variable()

        q = Query(safe(X, Y))

        while q.nextSolution():
            print(X.value, Y.value)
            cell = Cell(state=State.SAFE_UNVISITED)
            self.relative.path[(X.value, Y.value)] = cell
            
        q.closeQuery()