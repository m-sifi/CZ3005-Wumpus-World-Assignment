import sys
from map import *
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
    print_command("turnright / tr")
    print_command("turnleft / tl")
    print_command("moveforward / move")
    print_command("explore")
    print_command("shoot")
    print_command("pickup")
    print()

if __name__ == "__main__":
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")

    world = Map()
    relative_world = RelativeMap()

    world.data[1][4] = EntityType.PORTAL
    world.data[3][4] = EntityType.PORTAL
    world.data[4][5] = EntityType.PORTAL
    world.data[4][1] = EntityType.WUMPUS
    world.data[4][2] = EntityType.COIN

    prolog = Prolog()

    if len(sys.argv) > 1:
        prolog.consult(sys.argv[1])
    else:
        prolog.consult("data/agent.pl")

    print_help()

    while True:

        print(relative_world)

        print("? for help")
        action = input("> ") \
                    .strip()

        # Driver Commands
        if action in ["quit", "q"]:
            break

        elif action == "map":
            print(world)
            
        elif action == "?":
            print_help()

        # Agent Commands
        elif action in ["turnright", "tr"]:
            print("Turn Right")

        elif action in ["turnleft", "tl"]:
            print("Turn Left")
            
        elif action in ["moveforward", "move"]:
            print("Move")

        elif action == "explore":
            print("Explore")

        elif action == "shoot":
            print("Shoot")

        elif action == "pickup":
            print("Pickup")

        else:
            print("Invalid command")


