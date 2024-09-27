from old.STLNode import VariableNode, TemporalReducerNode, Window, Reducer

x = VariableNode("X")
y = VariableNode("Y")
reducer = Reducer(0, lambda a, b: a + b, lambda e: e[0] * e[1])
r = TemporalReducerNode(Window(1.5), reducer)
x.to(r.receive)

# s = BinaryNode(lambda a,b: a + b)
# x.to(s.receive_left)
# y.to(s.receive_right)
# ss = SumExpression()
# s.to(ss.receive_left)
# x.to(ss.receive_right)
r.to(lambda time, value: print("r", time, value))
# ss.to(lambda time, value: print("ss",time, value))


x.receive({"time": 0, "X": 0})
x.receive({"time": 1, "X": 7})
x.receive({"time": 2, "X": 2})
x.receive({"time": 3, "X": 3})
x.receive({"time": 4, "X": 4})

# y.receive({"time": 0, "Y": 12})
# y.receive({"time": 1, "Y": 15})
# y.receive({"time": 2, "Y": 12})
# x.receive({"time": 2, "X": 12})
# x.receive({"time": 2, "X": 12})
# y.receive({"time": 2, "Y": 13})
# x.receive({"time": 3, "X": 14})
# x.receive({"time": 4, "X": 12})
