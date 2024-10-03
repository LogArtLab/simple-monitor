from typing import List

from simplemonitor.mrl.nodes import SpatialReducerNode, Notifier, UnaryNode, BinaryNode, TemporalReducerNode, Window


class Memory:

    def __init__(self):
        super().__init__()
        self.observers = dict()
        self.memory = dict()

    def add_observer(self, from_variable, computation):
        if from_variable in self.observers:
            self.observers[from_variable].append(computation)
        else:
            self.observers[from_variable] = [computation, ]

    def receive(self, time, variable, value):
        self.memory[variable] = {"time": time, "value": value}
        for computation in self.observers.get(variable, []):
            computation(time, value)

    def get_value(self, variable):
        return self.memory.get(variable, None)


class Location:

    def __init__(self, name, state, world):
        super().__init__()
        self.memory = Memory()
        self.name = name
        self.world = world
        self.state = state

    def add_unary_node_computation(self, node, from_variable, to_variable):
        self.__add_computation_from(node.receive, from_variable)
        self.__add_computation_to(node, to_variable)

    def add_binary_node_computation(self, node, from_variable_left, from_variable_right, to_variable):
        self.__add_computation_from(node.receive_left, from_variable_left)
        self.__add_computation_from(node.receive_right, from_variable_right)
        self.__add_computation_to(node, to_variable)

    def add_spatial_reducer_node_computation(self, reducer, condition, from_variable, to_variable):
        locations = self.world.get_locations_satisfying_condition(from_location=self, condition=condition)
        node = SpatialReducerNode(reducer)
        node.add(self, from_variable)
        for location in locations:
            node.add(location, from_variable)
        self.__add_computation_to(node, to_variable)

    def add_observer(self, from_variable, notifier):
        self.memory.add_observer(from_variable, lambda time, value: notifier(self.name, from_variable, time, value))

    def __add_computation_from(self, computation, from_variable):
        self.memory.add_observer(from_variable, computation)

    def __add_computation_to(self, node: Notifier, to_variable):
        node.to(lambda time, value: self.memory.receive(time, to_variable, value))

    def receive(self, time, variable, value):
        self.memory.receive(time, variable, value)

    def get_name(self):
        return self.name

    def get_value(self, variable):
        return self.memory.get_value(variable)


class World:

    def __init__(self):
        super().__init__()
        self.locations = dict()

    def create_location(self, location_name, state):
        location = Location(location_name, state, self)
        self.locations[location_name] = location
        return location

    def add_unary_computation(self, operator, from_variable, to_variable):
        for location in self.locations.values():
            location.add_unary_node_computation(UnaryNode(operator), from_variable, to_variable)

    def add_binary_computation(self, operator, from_variable_left, from_variable_right, to_variable):
        for location in self.locations.values():
            location.add_binary_node_computation(BinaryNode(operator), from_variable_left, from_variable_right,
                                                 to_variable)

    def add_temporal_computation(self, length, reducer_generator, from_variable, to_variable):
        for location in self.locations.values():
            location.add_unary_node_computation(TemporalReducerNode(Window(length), reducer_generator()), from_variable,
                                                to_variable)

    def add_spatial_computation(self, reducer_generator, condition, from_variable, to_variable):
        for location in self.locations.values():
            location.add_spatial_reducer_node_computation(reducer_generator(), condition, from_variable, to_variable)

    def get_good_location_from(self, from_location, condition) -> List[Location]:
        good_locations = []
        for location in self.locations.values():
            if condition(location, from_location):
                good_locations.append(location)
        return good_locations

    def receive(self, location_name, time, variable, value):
        self.locations[location_name].receive(time, variable, value)

    def add_observer(self, from_variable, notifier):
        for location in self.locations.values():
            location.add_observer(from_variable, notifier)
