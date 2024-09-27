from old.nodes import VariableNode, Reducer, TemporalReducerNode, Window


def test_temporal_reducer():
    x = VariableNode("X")
    reducer = Reducer(0, lambda a, b: a + b, lambda e: e[0] * e[1])
    r = TemporalReducerNode(Window(1.0), reducer)
    x.to(r.receive)
    actual_values = []
    r.to(lambda time, value: actual_values.append((time, value)))

    x.receive({"time": 0.0, "X": 1})
    x.receive({"time": 0.5, "X": 2})
    x.receive({"time": 1.0, "X": 3})
    x.receive({"time": 1.5, "X": 4})
    x.receive({"time": 2.0, "X": 5})

    assert [(0.0, 1.5), (0.5, 2.5), (1.0, 3.5)] == actual_values
