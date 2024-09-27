# from simplemonitor.mrl.old.elements import LocationStorage, Location
#
#
# ## LOCATION STORAGE TESTS
# def test_add_location_with_all_cases():
#     l1 = Location("l1", {"X": 2})
#     l2 = Location("l2", {"X": 4})
#     l3 = Location("l3", {"X": 4.5})
#     location_storage = LocationStorage(lambda a, b: abs(a["X"] - b["X"]) < 1.9)
#
#     location_storage.add_location(l1)
#     location_storage.add_location(l2)
#     location_storage.add_location(l3)
#
#     assert {} == location_storage.get_children("l1")
#     assert ["l3", ] == location_storage.get_children("l2")
#     assert ["l2", ] == location_storage.get_children("l3")
#
#
# # LOCATION TESTS
# def test_location_get_value():
#     location = Location("name", {"content": "content_value"})
#
#     actual_value = location.get_value("content")
#
#     assert "content_value" == actual_value
#
#
# def test_get_name():
#     location = Location("name", {})
#
#     actual_name = location.get_name()
#
#     assert "name" == actual_name
