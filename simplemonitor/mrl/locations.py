from typing import List

from simplemonitor.mrl.elements import Memory, WindowInterval, Interval
from simplemonitor.mrl.functions import Polynomial
from simplemonitor.mrl.nodes import UnaryNode, BinaryNode, IntegralNode, NaryNode


class World:

    def __init__(self):
        super().__init__()
        self.locations = dict()
        self.buffer = dict()

    def create_location(self, location_name, state):
        location = Location(location_name, state, self)
        self.locations[location_name] = location
        self.buffer[location_name] = dict()
        return location

    def add_unary_computation(self, operator, from_variable, to_variable):
        for location in self.locations.values():
            location.add_unary_node_computation(UnaryNode(operator), from_variable, to_variable)

    def add_binary_computation(self, operator, from_variable_left, from_variable_right, to_variable):
        for location in self.locations.values():
            location.add_binary_node_computation(BinaryNode(operator), from_variable_left, from_variable_right,
                                                 to_variable)

    def add_integral_computation(self, length, from_variable, to_variable):
        for location in self.locations.values():
            location.add_unary_node_computation(IntegralNode(WindowInterval(length)), from_variable,
                                                to_variable)

    def add_spatial_computation(self, operator, condition, from_variable, to_variable):
        for location in self.locations.values():
            location.add_spatial_node_computation(NaryNode(operator), condition, from_variable, to_variable)

    def get_locations_satisfying_condition(self, from_location, condition) -> List['Location']:
        good_locations = []
        for location in self.locations.values():
            if condition(location, from_location) and location != from_location:
                good_locations.append(location)
        return good_locations

    def receive(self, location_name, variable, time, value):
        if variable not in self.buffer[location_name]:
            self.buffer[location_name][variable] = {"time": time, "value": value}
        else:
            data = self.buffer[location_name][variable]
            self.locations[location_name].receive(variable,
                                                  Interval(data["time"], time, Polynomial.constant(data["value"])))
            self.buffer[location_name][variable] = {"time": time, "value": value}

    def receive_interval(self, location_name, variable, interval):
        self.locations[location_name].receive(variable, interval)

    def add_observer(self, from_variable, notifier):
        for location in self.locations.values():
            location.add_observer(from_variable, notifier)


class Location:

    def __init__(self, name, state, world: World):
        super().__init__()
        self.memory = Memory()
        self.name = name
        self.world = world
        self.state = state

    def add_unary_node_computation(self, node: 'UnaryNode', from_variable: str, to_variable: str):
        self.memory.add_unary_node(from_variable, to_variable, node)

    def add_binary_node_computation(self, node: 'BinaryNode', from_variable_left, from_variable_right, to_variable):
        self.memory.add_binary_node(from_variable_left, from_variable_right, to_variable, node)

    def add_nary_node_computation(self, node: 'NaryNode', from_variable_list: List[str], to_variable):
        self.memory.add_nary_node(from_variable_list, to_variable, node)

    def add_spatial_node_computation(self, node: 'NaryNode', condition, from_variable, to_variable):
        locations = self.world.get_locations_satisfying_condition(self, condition)
        node.add_receiver(f"{self.name}-{from_variable}")
        self.memory.add_computation(from_variable,
                                    lambda interval, variable=f"{self.name}-{from_variable}": node.receive(
                                        variable, interval))
        for location in locations:
            node.add_receiver(f"{location.name}-{from_variable}")
            location.memory.add_computation(from_variable,
                                            lambda interval, variable=f"{location.name}-{from_variable}": node.receive(
                                                variable, interval))
        node.to(lambda interval: self.memory.receive(to_variable, interval))

    def add_observer(self, from_variable, notifier):
        self.memory.add_computation(from_variable, lambda interval: notifier(self.name, from_variable, interval))

    def receive(self, variable, interval):
        self.memory.receive(variable, interval)

    def get_name(self):
        return self.name

    def get_value(self, variable):
        return self.memory.get_value(variable)
