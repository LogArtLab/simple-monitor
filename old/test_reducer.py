from old.STLNode import Reducer


def test_temporal_reducer():
    temporal_reducer = Reducer(0, lambda a, b,: a + b, lambda e: e[0] * e[1])

    temporal_reducer.add((1, 2))
    temporal_reducer.add((3, 4))
    temporal_reducer.remove((1, 1))

    assert temporal_reducer.get_value() == 13


def test_spatial_reducer():
    spatial_reducer = Reducer(1, lambda a, b,: a * b)

    spatial_reducer.add(1)
    spatial_reducer.add(4)
    spatial_reducer.remove(2)

    assert spatial_reducer.get_value() == -8
