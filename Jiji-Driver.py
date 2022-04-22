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

if __name__ == "__main__":

    world = Map()
    world.data[1][5] = EntityType.PORTAL
    world.data[3][2] = EntityType.PORTAL
    world.data[4][5] = EntityType.PORTAL
    world.data[4][1] = EntityType.WUMPUS
    world.data[2][1] = EntityType.COIN

    world.agent_start = Agent(1, 1, Direction.NORTH)
    world.reset() # Resets put the agent at start position

    agent = "data/Jiji-Agent.pl"

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

        print(f"You have entered '{action}\n") # nl

        # Driver Commands
        if action in ["quit", "q"]:
            break
        elif action == "map":
            print(driver.map)
        elif action == "?":
            print_help()

        # Agent Commands
        elif action in ["turnright", "tr", "r"]:
            print("Action: Agent turn right")
            driver.turn_right()
        elif action in ["turnleft", "tl", "l"]:
            print("Action: Agent turn left")
            driver.turn_left()
        elif action in ["moveforward", "move", "f"]:
            print("Action: Agent move forward")
            driver.move_forward()
            print(driver.map)
        elif action in ["explore", "e"]:
            print("Action: Agent explore")
            driver.explore()
            print(driver.map)
        elif action in ["shoot", "s"]:
            print("Action: Agent shoot arrow")
            driver.shoot()
        elif action in ["pickup", "p"]:
            print("Action: Agent pickup coin (if any)")
            driver.pickup_coin()

        # Misc
        else:
            print("Invalid action")


