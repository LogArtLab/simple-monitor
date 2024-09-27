import math

from old.nodes import VariableNode, LocationNode, MiniWorld, SpatialReducerNode, Reducer


def distance(a, b):
    ds = (a[0] - b[0]) * (a[0] - b[0]) + (a[1] - b[1]) * (a[1] - b[1])
    return math.sqrt(ds)

distance_relation = lambda a, b: distance(a.state["P"], b.state["P"]) < 1.1
l1 = LocationNode("l1", {"P": (1, 1)})
l2 = LocationNode("l2", {"P": (1, 2)})
l3 = LocationNode("l3", {"P": (2, 1)})
l4 = LocationNode("l4", {"P": (2, 2)})
world = MiniWorld(distance_relation, lambda: SpatialReducerNode(Reducer(0, lambda a, b: a + b)))
world.add_location(l1)
world.add_location(l2)
world.add_location(l3)
world.add_location(l4)

x = VariableNode("X")
x.to(l1.receive)
x.to(l2.receive)
x.to(l3.receive)
x.to(l4.receive)

x.receive({"time": 0, "X": 0})
x.receive({"time": 1, "X": 1})
x.receive({"time": 2, "X": 2})
x.receive({"time": 3, "X": 3})
