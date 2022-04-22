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
            print("Agent bumped into a wall, ouch!")
            percept = self.map.percept(self.map.agent.x, self.map.agent.y)
            percept.bump = True

        if self.map.data[forward_y][forward_x] == EntityType.PORTAL:
            print("Agent stepped into a Portal and is confused?")
            self.reset()
            percept = self.map.percept(self.map.agent.x, self.map.agent.y)
            percept.confounded = True

        if self.map.has_wumpus(forward_x, forward_y):
            print("Agent stepped into a Wumpus and died of shock. Restarting world..")
            percept = Percept()
            percept.confounded = True
            self.restart()
            return

        list(self.prolog.query(f"move(moveforward, {percept})"))
        self.update(percept)

    def shoot(self):
        percept = self.map.percept(self.map.agent.x, self.map.agent.y)
        if self.map.agent.arrow:
            x = self.map.agent.x
            y = self.map.agent.y
            direction = self.map.agent.direction

            while self.map.is_valid(x, y):
                if self.map.has_wumpus(x, y):
                    self.map.wumpus[(x, y)] = False
                    percept.scream = True
                    break

                x, y = self.map.get_forward(x, y, direction)

        list(self.prolog.query(f"move(shoot, {percept})"))
        # Update Relative Map
        self.update(percept)

    def pickup_coin(self):
        percept = self.map.percept(self.map.agent.x, self.map.agent.y)

        if percept.glitter:
            percept.glitter = False
            self.map.coin[(self.map.agent.x, self.map.agent.y)] = False

        list(self.prolog.query(f"move(pickup, {percept})"))
        self.update(percept)

    def explore(self):
        try:
            path = list(self.prolog.query(f"explore(L)"))[0]["L"]
            print(path)

            for action in path:
                if action == "moveforward":
                    self.move_forward()
                elif action == "turnleft":
                    self.turn_left()
                elif action == "turnright":
                    self.turn_right()
        except:
            print("explore(L) returned nothing")

    def turn_left(self):
        percept = self.map.percept(self.map.agent.x, self.map.agent.y)

        list(self.prolog.query(f"move(turnleft, {percept})"))
        self.update(percept)

    def turn_right(self):
        percept = self.map.percept(self.map.agent.x, self.map.agent.y)

        list(self.prolog.query(f"move(turnright, {percept})"))
        self.update(percept)

    def update(self, percept):
        self.pl_safe()
        self.pl_unsafe()
        self.pl_percept()
        self.pl_wall()
        
        self.pl_current()

        self.relative.agent.percept = percept
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
            self.relative.agent.direction = Direction.NORTH
        elif direction == "reast":
            self.relative.agent.direction = Direction.EAST
        elif direction == "rsouth":
            self.relative.agent.direction = Direction.SOUTH
        elif direction == "rwest":
            self.relative.agent.direction = Direction.WEST

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

        q.closeQuery()

    def pl_safe(self):
        safe = list(self.prolog.query("safe(X, Y)"))
        unvisited = list(self.prolog.query("safe(X, Y), \+ visited(X, Y), \+ wall(X, Y)"))

        for result in safe:
            x = result["X"]
            y = result["Y"]
            self.relative.path[(x, y)] = State.SAFE_VISITED

        for result in unvisited:
            x = result["X"]
            y = result["Y"]
            self.relative.path[(x, y)] = State.SAFE_UNVISITED

    def pl_unsafe(self):
        wumpus = list(self.prolog.query("wumpus(X, Y)"))
        confundus = list(self.prolog.query("confundus(X, Y)"))
        unsafe = list(self.prolog.query("wumpus(X, Y), confundus(X, Y)"))

        for result in wumpus:
            x = result["X"]
            y = result["Y"]
            self.relative.path[(x, y)] = State.WUMPUS

        for result in confundus:
            x = result["X"]
            y = result["Y"]
            self.relative.path[(x, y)] = State.PORTAL

        for result in unsafe:
            x = result["X"]
            y = result["Y"]
            self.relative.path[(x, y)] = State.UNSAFE

    def pl_wall(self):
        query = list(self.prolog.query("wall(X, Y)"))

        for result in query:
            x = result["X"]
            y = result["Y"]
            self.relative.path[(x, y)] = State.WALL

    def pl_percept(self):
        stench = list(self.prolog.query("stench(X, Y)"))
        glitter = list(self.prolog.query("glitter(X, Y)"))
        tingle = list(self.prolog.query("tingle(X, Y)"))

        self.relative.stench.clear()
        self.relative.glitter.clear()
        self.relative.tingle.clear()

        for item in stench:
            self.relative.stench.add((item["X"], item["Y"]))

        for item in glitter:
            self.relative.glitter.add((item["X"], item["Y"]))

        for item in tingle:
            self.relative.tingle.add((item["X"], item["Y"]))


    def safe(self, x, y):
        return bool(list(self.prolog.query(f"safe({x}, {y})")))

    def visited(self, x, y):
        return bool(list(self.prolog.query(f"visited({x}, {y})")))

    def pl_listing(self, query):
        print(f"{query}: {list(self.prolog.query(query))}")