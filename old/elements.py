#
#
#
# class Reducer:
#
#     def __init__(self, value, aggregator, function=lambda x: x):
#         self.value = value
#         self.aggregator = aggregator
#         self.function = function
#
#     def get_value(self):
#         return self.value
#
#     def add(self, element):
#         self.value = self.aggregator(self.value, self.function(element))
#
#     def remove(self, element):
#         self.value = self.aggregator(self.value, -self.function(element))
#
#
# class Location:
#
#     def __init__(self, name, content):
#         super().__init__()
#         self.name = name
#         self.content = content
#
#     def get_value(self, variable):
#         return self.content[variable]
#
#     def get_values(self):
#         return self.content
#
#     def get_name(self):
#         return self.name
#
#
# class LocationStorage:
#
#     def __init__(self, relation, reducer_generator=lambda: None, reducer_variable=None):
#         super().__init__()
#         self.reducer_variable = reducer_variable
#         self.reducer_generator = reducer_generator
#         self.children = dict()
#         self.locations = dict()
#         self.relation = relation
#         self.last_update = None
#         self.update_contents = []
#         self.reducers = dict()
#
#     def add_location(self, new_location: Location):
#         for location in self.locations.values():
#             if self.relation(new_location.get_values(), location.get_values()):
#                 self.__add_child_to_parent(new_location, location)
#                 self.__add_child_to_parent(location, new_location)
#         self.locations[new_location.get_name()] = new_location
#         self.reducers[new_location.get_name()] = self.reducer_generator()
#
#     def __add_child_to_parent(self, child: Location, parent: Location):
#         parent_name = parent.get_name()
#         children = self.children.get(parent_name, [])
#         children.append(child.get_name())
#         self.children[parent_name] = children
#
#     def get_children(self, location_name):
#         return self.children.get(location_name, {})
#
#     def update(self, time, update_content):
#         if time != self.last_update and not self.update_contents:
#             self.__perform_update()
#             self.update_contents = []
#         else:
#             self.last_update = time
#             self.update_contents.append(update_content)
#
#     def __perform_update(self):
#         for update_content in self.update_contents:
#             update_location_name = update_content["name"]
#             update_location = self.locations[update_location_name]
#             for child_location_name in self.children[update_location_name]:
#                 child_location = self.locations[child_location_name]
#                 if not self.relation(update_location, child_location):
#                     pass
