from old.STLNode import Location
from old.elements import LocationStorage


def test_location():
    l1 = Location("one")
    l2 = Location("two")
    l1.to(lambda data: print(data))
    l2.to(lambda data: print(data))

    r1 = l1.get_receiver("X")
    r2 = l2.get_receiver("X")

    r1(0, 0)
    r2(1, 1)
    r1(2, 2)
    r2(3, 3)


def test_location_storage():
    l1 = {"name": "l1", "X": 2}
    l2 = {"name": "l2", "X": 4}
    location_storage = LocationStorage(lambda a, b: abs(a["X"] - b["X"]) < 1.9)

    location_storage.add_location(l1)
    location_storage.add_location(l2)

    print()
