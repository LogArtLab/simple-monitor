from simplemonitor.mrl.functions import Polynomial
from simplemonitor.mrl.utility import mean_polynomial
from simplemonitor.mrl.elements import Interval
from simplemonitor.mrl.locations import World

world = World()
world.create_location("l1", {"P": 1})
world.create_location("l2", {"P": 2})
world.create_location("l3", {"P": 3})

# X -> 3X
world.add_unary_computation(lambda f: f + 3, "X", "X+3")
#
# # 3X,Y -> Z = 3X+Y
# world.add_binary_computation(lambda f, g: f + g, "3X", "Y", "Z")

condition = lambda la, lb: abs(la.state["P"] - lb.state["P"]) < 1.5

world.add_spatial_computation(mean_polynomial, condition, "X+3", "MEAN")

world.add_observer("X+3", lambda location_name, variable, interval: print(location_name, variable, interval))
world.add_observer("Z", lambda location_name, variable, interval: print(location_name, variable, interval))
world.add_observer("MEAN", lambda location_name, variable, interval: print(location_name, variable, interval))

world.receive("l1", "X", 1, 2)
world.receive("l1", "X", 2, 3)
world.receive("l2", "X", 1, 1)
world.receive("l2", "X", 2, 3)
world.receive("l3", "X", 1, 1)
world.receive("l3", "X", 2, 3)

# world.receive("l1", "X", Interval(2, 7, Polynomial.linear(1, 2)))
# world.receive("l1", "Y", Interval(1, 6, Polynomial.constant(2)))
#
# world.receive("l2", "X", Interval(2, 7, Polynomial.linear(1, 2)))
# world.receive("l2", "Y", Interval(1, 6, Polynomial.constant(2)))
