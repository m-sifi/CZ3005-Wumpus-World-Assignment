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

        if self.map.has_wumpus(forward_x, forward_y):
            percept = Percept()
            percept.confounded = True

            self.restart()
            # self.update(percept)
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
        # Update Relative Map
        self.update(percept)

    def explore(self):
        try:
            path = list(self.prolog.query(f"once(explore(L))"))[0]["L"]
            print(path)

            for action in path:
                if action == "moveforward":
                    self.move_forward()
                elif action == "turnleft":
                    self.turn_left()
                elif action == "turnright":
                    self.turn_right()
                # elif action == "pickup":
                #     print("Pick")
                #     self.pickup_coin()

                self.pickup_coin()
        except:
            # print(list(self.prolog.query(f"glitter(X, Y)")))
            pass

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
        self.pl_safe()
        self.pl_unsafe()
        self.pl_percept()
        # self.pl_wumpus()
        # self.pl_portal()
        self.pl_wall()
        self.pl_current()

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
        query = list(self.prolog.query("safe(X, Y)"))
        subquery = list(self.prolog.query("visited(X, Y)"))

        for result in query:
            x = result["X"]
            y = result["Y"]
            cell = Cell(state=State.SAFE_UNVISITED)

            if result in subquery:
                cell = Cell(state=State.SAFE_VISITED)

            self.relative.path[(x, y)] = cell

    def pl_unsafe(self):
        query = list(self.prolog.query("wumpus(X, Y)"))
        subquery = list(self.prolog.query("confundus(X, Y)"))

        for result in query:
            x = result["X"]
            y = result["Y"]
            cell = Cell(state=State.WUMPUS)

            if result in subquery:
                cell = Cell(state=State.UNSAFE)

            self.relative.path[(x, y)] = cell

        for result in subquery:
            x = result["X"]
            y = result["Y"]

            if (x, y) not in self.relative.path:
                self.relative.path[(x, y)] = Cell(state=State.PORTAL)


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