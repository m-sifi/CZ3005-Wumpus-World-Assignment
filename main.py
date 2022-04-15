import sys
from map import *
from driver import *
from pyswip.easy import *
from pyswip import Prolog

def print_command(commands, description = ""):
    if description:
        print(f"- {commands} : {description}")
    else:
        print(f"- {commands}")

def print_help():
    print("\n== Commands ==")
    print_command("map", "Prints absolute map")
    print_command("quit / q", "Closes driver and terminate program")
    print_command("?", "Prints out help")

    print("\n== Agent Commands ==")
    print_command("turnright / tr / r")
    print_command("turnleft / tl / l")
    print_command("moveforward / move/ f")
    print_command("explore / e")
    print_command("shoot / s")
    print_command("pickup / p")
    print()

def move_forward(world: Map):
    prolog = Prolog()
    pl_move = Functor("move", 2)
    percept = world.percept(world.agent.x, world.agent.y)

    forward_x, forward_y = world.agent_forward()

    if world.data[forward_y][forward_x] == EntityType.WALL:
        percept.bump = True

    list(prolog.query(f"move(moveforward, {percept})"))
    return percept

if __name__ == "__main__":

    world = Map()
    world.data[1][4] = EntityType.PORTAL
    world.data[3][4] = EntityType.PORTAL
    world.data[4][5] = EntityType.PORTAL
    world.data[4][1] = EntityType.WUMPUS
    world.data[4][2] = EntityType.COIN

    world.agent_start = Agent(1, 1, Direction.NORTH)
    world.reset() # Resets put the agent at start position

    agent = "data/agent.pl"

    if len(sys.argv) > 1:
        agent = sys.argv[1]

    driver = WumpusDriver(world, agent)

    print(driver.map)
    print_help()

    while True:
        print(driver.relative)

        print("? for help")
        action = input("> ") \
                    .strip()

        # Driver Commands
        if action in ["quit", "q"]:
            break
        elif action == "map":
            print(driver.map)
        elif action == "?":
            print_help()

        # Agent Commands
        elif action in ["turnright", "tr", "r"]:
            driver.turn_right()
        elif action in ["turnleft", "tl", "l"]:
            driver.turn_left()
            pass
        elif action in ["moveforward", "move", "f"]:
            driver.move_forward()
        elif action in ["explore", "e"]:
            print("Explore")
        elif action in ["shoot", "s"]:
            print("Shoot")
        elif action in ["pickup", "p"]:
            print("Pickup")

        # Misc
        else:
            print("Invalid command")


