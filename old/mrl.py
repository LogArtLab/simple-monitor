













class SpatialReducerGlobalNode:

    def __init__(self, condition, condition_variables, from_variable, to_variable):
        self.to_variable = to_variable
        self.from_variable = from_variable
        self.condition_variables = condition_variables
        self.condition = condition
        self.location_reducers = dict()
        self.locations = dict()
        self.location_groups = dict()
        self.location_values = dict()

    def add_location(self, new_location: Location, reducer):
        self.location_reducers[new_location.get_name()] = reducer
        for location in self.locations.values():
            if self.__location_has_condition_variables(location) and self.__location_has_condition_variables(
                    new_location) and self.condition(location, new_location):
                group = self.location_groups.get(location.get_name(), [])
                group.append(new_location)
                self.location_groups[new_location.get_name()] = [location, ]
        self.locations[new_location.get_name()] = new_location
        self.location_values[new_location.get_name()] = None
        for variable in self.condition_variables:
            new_location.add_observer(variable, self.receive)
        new_location.add_observer(self.from_variable, self.receive)

    def __location_has_condition_variables(self, location):
        for variable in self.condition_variables:
            if location.get_value(variable) is None:
                return False
        return True and location.get_value(self.from_variable) is not None

    def __update_reducer(self, time, location_name, old_value, new_value):
        reducer = self.location_reducers[location_name]
        if old_value is not None:
            reducer.remove(old_value)
        reducer.add(new_value)
        self.locations[location_name].receive(time, self.to_variable, reducer.get_value())

    def receive(self, location_name, variable, time, value):
        if variable == self.from_variable:
            old_value = self.location_values[location_name]
            self.__update_reducer(time, location_name, old_value, value)
            for location in self.location_groups.get(location_name, []):
                self.__update_reducer(time, location.get_name(), old_value, value)
            self.location_values[location_name] = value
        if variable in self.condition_variables:
            for location in self.location_groups.get(location_name, []):
                parent_location = self.locations[location_name]
                if self.__location_has_condition_variables(location) and self.__location_has_condition_variables(
                        parent_location) and not self.condition(location, parent_location):
                    self.__remove_location(time, location, parent_location)
                    self.__remove_location(time, parent_location, location)
            for location in set(self.locations.values()) - set(self.location_groups.get(location_name, [])) - {
                self.locations[location_name]}:
                parent_location = self.locations[location_name]
                if self.__location_has_condition_variables(location) and self.__location_has_condition_variables(
                        parent_location) and self.condition(location, parent_location):
                    self.__add_location(time, location, parent_location)
                    self.__add_location(time, parent_location, location)

    def __remove_location(self, time, child_location, parent_location):
        reducer = self.location_reducers[parent_location.get_name()]
        reducer.remove(self.location_values[child_location.get_name()])
        self.location_groups[parent_location.get_name()].remove(child_location)
        parent_location.receive(time, self.to_variable, reducer.get_value())

    def __add_location(self, time, child_location, parent_location):
        reducer = self.location_reducers[parent_location.get_name()]
        reducer.add(self.location_values[child_location.get_name()])
        if parent_location.get_name() in self.location_groups:
            self.location_groups[parent_location.get_name()].append(child_location)
        else:
            self.location_groups[parent_location.get_name()] = [child_location, ]
        parent_location.receive(time, self.to_variable, reducer.get_value())





class UnaryFormula:

    def __init__(self, name, operator, child):
        self.operator = operator
        self.child = child
        self.name = name

    def visit(self, location: Location):
        location.add_unary_node_computation(UnaryNode(self.operator), self.child.get_name(), self.get_name())
        self.child.visit(location)

    def get_name(self):
        return self.name


class BinaryFormula:

    def __init__(self, name, operator, left_child, right_child):
        self.operator = operator
        self.left_child = left_child
        self.right_child = right_child
        self.name = name

    def visit(self, location: Location):
        location.add_binary_node_computation(BinaryNode(self.operator), self.left_child.get_name(),
                                             self.right_child.get_name(), self.get_name())
        self.left_child.visit(location)
        self.right_child.visit(location)

    def get_name(self):
        return self.name


class VariableFormula:

    def __init__(self, name):
        self.name = name

    def visit(self, location: Location):
        pass

    def get_name(self):
        return self.name


class TemporalReducerFormula:

    def __init__(self, name, length, reducer_generator, child):
        self.length = length
        self.child = child
        self.name = name
        self.reducer_generator = reducer_generator

    def visit(self, location: Location):
        node = TemporalReducerNode(Window(self.length), self.reducer_generator())
        location.add_unary_node_computation(node, self.child.get_name(), self.get_name())
        self.child.visit(location)

    def get_name(self):
        return self.name


class SpatialReducerFormula:
    def __init__(self, name, reducer_generator, condition, child):
        self.name = name
        self.condition = condition
        self.reducer_generator = reducer_generator
        self.child = child

    # def visit(self, location: Location):
    #     location.add_spatial_reducer_node_computation(self.reducer_generator(), self.condition, self.child.get_name(),
    #                                                   self.get_name())
    #     self.child.visit(location)

    def get_name(self):
        return self.name



