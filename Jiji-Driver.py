import sys
from map import *
from driver import *
from pyswip.easy import *
from pyswip import Prolog

AGENT_FILE = "data/Jiji-Agent.pl"

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

def run_action(driver, action):
    # Agent Commands
    if action in ["turnright", "tr", "r"]:
        print("Action: Agent turn right")
        driver.turn_right()
    elif action in ["turnleft", "tl", "l"]:
        print("Action: Agent turn left")
        driver.turn_left()
    elif action in ["moveforward", "move", "f"]:
        print("Action: Agent move forward")
        driver.move_forward()
        # print(driver.map)
    elif action in ["explore", "e"]:
        print("Action: Agent explore")
        driver.explore()
        # print(driver.map)
    elif action in ["shoot", "s"]:
        action("Action: Agent shoot arrow")
        driver.shoot()
    elif action in ["pickup", "p"]:
        print("Action: Agent pickup coin (if any)")
        driver.pickup_coin()

def run_test(printout):

    sys.stdout = open(file=printout, mode="w", encoding="utf8")

    world = Map()
    world.data[1][5] = EntityType.PORTAL
    world.data[3][2] = EntityType.PORTAL
    world.data[4][5] = EntityType.PORTAL
    world.data[4][1] = EntityType.WUMPUS
    world.data[2][1] = EntityType.COIN

    world.agent_start = Agent(1, 1, Direction.NORTH)
    world.reset() # Resets put the agent at start position

    agent = AGENT_FILE

    if len(sys.argv) > 1:
        agent = sys.argv[1]

    driver = WumpusDriver(world, agent)

    mapping_test(driver)
    confundus_test(driver)
    wumpus_test(driver)
    explore_test(driver)

def mapping_test(driver):

    driver.restart()

    print("\n\n\n")
    print("== Testing Agent Mapping and Localisation Correctness ==")
    print("\n\n\n")


    actions = ["moveforward", "moveforward", "turnright", "turnright", "moveforward", "turnleft", "moveforward", "moveforward", "turnleft", "moveforward", "moveforward", "moveforward"]

    print(driver.map)
    print(driver.relative)
    print()

    for item in actions:
        run_action(driver, item)
        
        print(driver.map)
        print(driver.relative)
        print()

def confundus_test(driver):

    driver.restart()

    print("\n\n\n")
    print("== Testing Agent stepping into Portal ==")
    print("\n\n\n")

    actions = ["moveforward", "moveforward", "turnright", "moveforward"]

    print(driver.map)
    print(driver.relative)
    print()

    for item in actions:
        run_action(driver, item)
        
        print(driver.map)
        print(driver.relative)
        print()

def wumpus_test(driver):


    driver.map.agent_start.x = 1
    driver.map.agent_start.y = 1
    driver.map.agent_start.direction = Direction.NORTH

    driver.restart()

    print("\n\n\n")
    print("== Testing Agent End-Game Reset ==")
    print("\n\n\n")

    actions = ["moveforward", "moveforward", "moveforward" ]

    print(driver.map)
    print(driver.relative)
    print()

    for item in actions:
        run_action(driver, item)
        
        print(driver.map)
        print(driver.relative)
        print()

def explore_test(driver):

    driver.restart()

    print("\n\n\n")
    print("== Testing Exploration Capabilities ==")
    print("\n\n\n")

    print(driver.map)
    print(driver.relative)
    print()

    result = driver.explore()

    while result:
        print(driver.map)
        print(driver.relative)
        print()

        driver.pickup_coin()
        result = driver.explore()

def manual_run():
    world = Map()
    world.data[1][5] = EntityType.PORTAL
    world.data[3][2] = EntityType.PORTAL
    world.data[4][5] = EntityType.PORTAL
    world.data[4][1] = EntityType.WUMPUS
    world.data[2][1] = EntityType.COIN

    world.agent_start = Agent(1, 1, Direction.NORTH)
    world.reset() # Resets put the agent at start position

    agent = AGENT_FILE

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


if __name__ == "__main__":
    # manual_run()
    run_test("Jiji-testPrintout-<agent source>-<driver source>.txt")