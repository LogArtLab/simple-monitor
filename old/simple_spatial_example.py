from old.locations import World
from simplemonitor.mrl.nodes import Reducer
from simplemonitor.mrl.utility import BufferedObserver

world = World()
world.create_location("l1", {"P": 1})
world.create_location("l2", {"P": 2})

# X -> 3X
world.add_unary_computation(lambda x: 3 * x, "X", "3X")

# 3X,Y -> Z = 3X+Y
world.add_binary_computation(lambda x, y: x + y, "3X", "Y", "Z")

# SUM_condition(Z)
condition = lambda la, lb: abs(la.state["P"] - lb.state["P"]) < 2
world.add_spatial_computation(lambda: Reducer(0, lambda x, y: x + y), condition, "Z", "RZ")

world.add_observer("RZ", BufferedObserver(
    lambda location_name, variable, time, value: print(variable, location_name, time, value)).receive)

world.receive("l1", 0, "X", 1)
world.receive("l1", 0, "Y", 1)
world.receive("l2", 0, "X", 1)
world.receive("l2", 0, "Y", 1)

world.receive("l1", 0.5, "X", 2)
world.receive("l1", 0.5, "Y", 2)
world.receive("l2", 0.5, "X", 2)
world.receive("l2", 0.7, "Y", 2)

world.receive("l1", 1, "X", 3)
world.receive("l1", 1, "Y", 3)
world.receive("l2", 1, "X", 3)
world.receive("l2", 1, "Y", 3)
