from old.STLNode import VariableNode, TemporalReducerNode, Window, Reducer, SpatialReducerNode

l1_x = VariableNode("X")
l1_reducer = Reducer(0, lambda a, b: a + b, lambda e: e[0] * e[1])
l1_r = TemporalReducerNode(Window(1.5), l1_reducer)
l1_x.to(l1_r.receive)
l2_x = VariableNode("X")
l2_reducer = Reducer(0, lambda a, b: a + b, lambda e: e[0] * e[1])
l2_r = TemporalReducerNode(Window(1.5), l2_reducer)
l2_x.to(l2_r.receive)

sr = SpatialReducerNode(Reducer(0, lambda a, b: a + b))
l2_r.to(sr.get_receiver("lr2"))
l1_r.to(sr.get_receiver("lr1"))

sr.to(lambda time, value: print("r", time, value))

l1_x.receive({"time": 0, "X": 0})
l2_x.receive({"time": 1, "X": 7})
l1_x.receive({"time": 2, "X": 2})
l2_x.receive({"time": 3, "X": 7})
l1_x.receive({"time": 4, "X": 2})