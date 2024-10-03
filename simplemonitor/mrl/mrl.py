from typing import Tuple, List

from simplemonitor.mrl.functions import Polynomial


class Interval:

    def __init__(self, start: float, end: float, function: Polynomial):
        self.start = start
        self.end = end
        self.function = function

    def length(self) -> float:
        return self.end - self.start

    def split(self, time) -> Tuple['Interval', 'Interval']:
        split_time = self.start + time
        return Interval(self.start, split_time, self.function), Interval(split_time, self.end, self.function)

    def __repr__(self):
        return f"[{self.start} - {self.end}] | {self.function}"

    def __add__(self, other: 'Interval') -> 'Interval':
        if (self.start, self.end) != (other.start, other.end):
            raise Exception("Cannot sum interval with different bounds")
        return Interval(self.start, self.end, self.function + other.function)

    def __sub__(self, other: 'Interval') -> 'Interval':
        if (self.start, self.end) != (other.start, other.end):
            raise Exception("Cannot subtract interval with different bounds")
        return Interval(self.start, self.end, self.function - other.function)

    def __eq__(self, other: 'Interval'):
        return (self.start, self.end) == (other.start, other.end) and self.function == other.function

    def integrate(self) -> float:
        integral_function = self.function.integral()
        return integral_function(self.end) - integral_function(self.start)

    def integral(self) -> 'Interval':
        return Interval(self.start, self.end, self.function.integral())

    def move_above(self, interval: 'Interval'):
        delta = self.start - interval.start
        return Interval(interval.start, interval.end, self.function.move(delta))

    def zeros(self, interval: 'Interval'):
        return (self.function - interval.function).zeros()

    def apply_operator(self, operator) -> 'Interval':
        return Interval(self.start, self.end, operator(self.function))

    def apply_binary_operator(self, operator, other: 'Interval') -> 'Interval':
        if (self.start, self.end) != (other.start, other.end):
            raise Exception("Cannot apply binary operator between intervals with different bounds")
        return Interval(self.start, self.end, operator(self.function, other.function))


class IntervalNotifier:

    def __init__(self):
        self.observers = []

    def to(self, observer):
        self.observers.append(observer)

    def notify(self, interval: 'Interval'):
        for observer in self.observers:
            observer(interval)


class UnaryNode(IntervalNotifier):

    def __init__(self, operator):
        super().__init__()
        self.left = None
        self.right = None
        self.operator = operator

    def receive(self, interval: 'Interval'):
        self.notify(interval.apply_operator(self.operator))


class BinaryNode(IntervalNotifier):

    def __init__(self, operator):
        super().__init__()
        self.left = []
        self.right = []
        self.operator = operator

    def __merge(self):
        right = self.right[0]
        left = self.left[0]
        if right.start < left.start:
            self.notify(Interval(right.start, left.start, Polynomial.undefined()))
            right.start = left.start
        elif left.start < right.start:
            self.notify(Interval(left.start, right.start, Polynomial.undefined()))
            left.start = right.start
        elif left.end < right.end:
            right_left, right_right = right.split(left.end - right.start)
            self.right[0] = right_right
            self.left.pop(0)
            self.notify(left.apply_binary_operator(self.operator, right_left))
        elif right.end < left.end:
            left_left, left_right = left.split(right.end - left.start)
            self.left[0] = left_right
            self.right.pop(0)
            self.notify(right.apply_binary_operator(self.operator, left_left))
        else:
            self.left.pop(0)
            self.right.pop(0)
            self.notify(right.apply_binary_operator(self.operator, left))

    def receive_left(self, interval: 'Interval'):
        self.left.append(interval)
        while len(self.left) > 0 and len(self.right) > 0:
            self.__merge()

    def receive_right(self, interval: 'Interval'):
        self.right.append(interval)
        while len(self.left) > 0 and len(self.right) > 0:
            self.__merge()


class WindowIntervalNotifier:
    def __init__(self):
        self.observers = []

    def to(self, observer):
        self.observers.append(observer)

    def notify_addition(self, interval):
        for observer in self.observers:
            observer.add(interval)

    def notify_move(self, interval_to_remove, interval_to_add):
        for observer in self.observers:
            observer.move(interval_to_remove, interval_to_add)


class WindowInterval(WindowIntervalNotifier):

    def __init__(self, length):
        super().__init__()
        self.intervals = []
        self.acc_length = 0
        self.right_interval = None
        self.length = length

    def add(self, interval: 'Interval'):
        interval_length = interval.length()
        remaining_length = self.length - self.acc_length
        if interval_length <= remaining_length:
            self.intervals.append(interval)
            self.acc_length += interval_length
            self.notify_addition(interval)
            return
        elif remaining_length > 0:
            to_be_added, interval_to_move = interval.split(remaining_length)
            self.intervals.append(to_be_added)
            self.acc_length += to_be_added.length()
            self.right_interval = interval_to_move
            self.notify_addition(to_be_added)
        else:
            self.right_interval = interval
        while self.right_interval is not None:
            self.__move()

    def __move(self):
        left_interval = self.intervals[0]
        left_interval_length = left_interval.length()
        right_interval_length = self.right_interval.length()
        right_minus_left_length = right_interval_length - left_interval_length
        if right_minus_left_length > 0:
            to_be_added, self.right_interval = self.right_interval.split(left_interval_length)
            to_be_removed = self.intervals.pop(0)
            self.intervals.append(to_be_added)
            self.notify_move(to_be_removed, to_be_added)
        elif right_minus_left_length == 0:
            to_be_added = self.right_interval
            to_be_removed = self.intervals.pop(0)
            self.right_interval = None
            self.intervals.append(to_be_added)
            self.notify_move(to_be_removed, to_be_added)
        else:
            to_be_removed, self.intervals[0] = left_interval.split(right_interval_length)
            to_be_added = self.right_interval
            self.right_interval = None
            self.intervals.append(to_be_added)
            self.notify_move(to_be_removed, to_be_added)


class Integral:
    def __init__(self):
        super().__init__()
        self.value = 0

    def add(self, interval: Interval):
        self.value += interval.integrate()

    def move(self, removed: Interval, added: Interval):
        added_above = added.move_above(removed)
        zero = removed.zeros(added_above)[0]
        if zero is not None and removed.end > zero > removed.start:
            removed_left, removed_right = removed.split(zero)
            added_above_left, added_above_right = added_above.split(zero)
            left = added_above_left.integral() - (removed_left.integral()) + Interval(removed_left.start,
                                                                                      removed_left.end,
                                                                                      Polynomial.constant(
                                                                                          self.value))
            right = added_above_right.integral() - (removed_right.integral()) + Interval(removed_right.start,
                                                                                         removed_right.end,
                                                                                         Polynomial.constant(
                                                                                             self.value))
            return left, right

        else:
            return (added_above.integral() - (removed.integral()) + Interval(removed.start, removed.end,
                                                                             Polynomial.constant(
                                                                                 self.value)),)


class IntegralNode(IntervalNotifier):
    def __init__(self, window: WindowInterval):
        super().__init__()
        window.to(self)
        self.window = window
        self.integral = Integral()

    def add(self, interval: Interval):
        self.integral.add(interval)

    def move(self, removed: Interval, added: Interval):
        results = self.integral.move(removed, added)
        for result in results:
            self.notify(result)

    def receive(self, interval: Interval):
        self.window.add(interval)


class Memory:

    def __init__(self):
        super().__init__()
        self.observers = dict()
        self.memory = dict()

    def add_computation(self, from_variable, computation):
        if from_variable in self.observers:
            self.observers[from_variable].append(computation)
        else:
            self.observers[from_variable] = [computation, ]

    def receive(self, variable, interval):
        self.memory[variable] = interval
        for computation in self.observers.get(variable, []):
            computation(interval)

    def get_value(self, variable):
        return self.memory.get(variable, None)

    def add_unary_node(self, from_variable, to_variable, node):
        self.add_computation(from_variable, node.receive)
        node.to(lambda interval: self.receive(to_variable, interval))

    def add_binary_node(self, from_variable_left, from_variable_right, to_variable, node):
        self.add_computation(from_variable_left, node.receive_left)
        self.add_computation(from_variable_right, node.receive_right)
        node.to(lambda interval: self.receive(to_variable, interval))

    def add_nary_node(self, from_variable_list: List[str], to_variable, node: 'NaryNode'):
        for from_variable in from_variable_list:
            node.add_receiver(from_variable)
            self.add_computation(from_variable,
                                 lambda interval, variable=from_variable: node.receive(variable, interval))
        node.to(lambda interval: self.receive(to_variable, interval))


class NaryNode(IntervalNotifier):

    def __init__(self, operator):
        super().__init__()
        self.locations = dict()
        self.operator = operator

    # def __get_location_from_name(self, location_name):
    #     if location_name not in self.locations:
    #         self.locations[location_name] = []
    #     return self.locations[location_name]

    def __should_merge(self):
        for locations in self.locations.values():
            if not locations:
                return False
        return True

    def add_receiver(self, location_name):
        self.locations[location_name] = []

    def receive(self, location_name, interval):
        locations = self.locations[location_name]
        locations.append(interval)
        while self.__should_merge():
            self.__merge()

    def __merge(self):
        starts = [l[0].start for l in self.locations.values()]
        end = [l[0].end for l in self.locations.values()]
        min_starts = min(starts)
        max_starts = max(starts)
        if min_starts != max_starts:
            self.notify(Interval(min_starts, max_starts, Polynomial.undefined()))
            for l in self.locations:
                l[0] = l[0].split(max_starts - min_starts)[1]
        min_end = min(end)
        cut = []
        for l in self.locations.values():
            l_end = l[0].end
            if l_end > min_end:
                l_left, l_right = l[0].split(min_end - l[0].start)
                cut.append(l_left)
                l[0] = l_right
            else:
                cut.append(l.pop(0))
        self.notify(self.operator(cut))


def mean_polynomial(interval: List[Interval]):
    result = interval[0]
    n = len(interval)
    for i in range(1, n):
        result = result + interval[i]
    rf = result.function
    return Interval(result.start, result.end, Polynomial(rf.a / n, rf.b / n, rf.c / n))


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
