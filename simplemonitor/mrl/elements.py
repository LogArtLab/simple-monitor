from typing import Tuple, List

from simplemonitor.mrl.functions import Polynomial
from simplemonitor.mrl.notifiers import WindowIntervalNotifier

EPS = 1e-5


def are_numerically_equivalent(a, b):
    return abs(a - b) < EPS


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
        return (are_numerically_equivalent(self.start, other.start)
                and are_numerically_equivalent(self.end, other.end)
                and self.function == other.function
                )

    def integrate(self) -> float:
        integral_function = self.function.integral()
        return integral_function(self.end) - integral_function(self.start)

    def integral(self) -> 'Interval':
        return Interval(self.start, self.end, self.function.integral())

    def move_above(self, interval: 'Interval'):
        delta = self.start - interval.start
        return Interval(interval.start, interval.end, self.function.move(delta))

    def project_onto(self, other: 'Interval'):
        if self.start > other.start or self.end < other.end:
            raise Exception("Cannot project onto bigger intervals")
        return Interval(other.start, other.end, self.function)

    def zeros(self, interval: 'Interval'):
        zeros = (self.function - interval.function).zeros()
        return [zero for zero in zeros if self.start <= zero <= self.end]

    def apply_operator(self, operator) -> 'Interval':
        return Interval(self.start, self.end, operator(self.function))

    def apply_binary_operator(self, operator, other: 'Interval') -> 'Interval':
        if (self.start, self.end) != (other.start, other.end):
            raise Exception("Cannot apply binary operator between intervals with different bounds")
        return Interval(self.start, self.end, operator(self.function, other.function))

    def get_extreme_value(self) -> Tuple[float, float]:
        return self.function(self.start), self.function(self.end)

    def is_increasing(self):
        left_value, right_value = self.get_extreme_value()
        return left_value < right_value

    def is_decreasing(self):
        left_value, right_value = self.get_extreme_value()
        return right_value < left_value

    def is_constant(self):
        left_value, right_value = self.get_extreme_value()
        return right_value == left_value

    def min_interval(self, other) -> List['Interval']:
        if (self.start, self.end) != (other.start, other.end):
            raise Exception("Cannot apply binary operator between intervals with different bounds")
        self_extreme = self.get_extreme_value()
        other_extreme = other.get_extreme_value()
        zeros = self.zeros(other)
        if not zeros:
            if self_extreme[0] <= other_extreme[0]:
                return [self, ]
            else:
                return [other, ]
        min_interval = list()
        extended_zeros = [self.start, ] + zeros + [self.end, ]
        functions = [self.function, other.function]
        if self_extreme[0] <= other_extreme[0]:
            for i in range(len(extended_zeros) - 1):
                min_interval.append(Interval(extended_zeros[i], extended_zeros[i + 1], functions[i % 2]))
        else:
            for i in range(len(extended_zeros) - 1):
                min_interval.append(Interval(extended_zeros[i], extended_zeros[i + 1], functions[(i + 1) % 2]))
        return min_interval


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

    def add_nary_node(self, from_variable_list: List[str], to_variable, node):
        for from_variable in from_variable_list:
            node.add_receiver(from_variable)
            self.add_computation(from_variable,
                                 lambda interval, variable=from_variable: node.receive(variable, interval))
        node.to(lambda interval: self.receive(to_variable, interval))


class Integral:
    def __init__(self):
        super().__init__()
        self.value = 0

    def add(self, interval: Interval):
        self.value += interval.integrate()

    def move(self, removed: Interval, added: Interval):
        added_above = added.move_above(removed)
        zeros = removed.zeros(added_above)
        if zeros and removed.end > zeros[0] > removed.start:
            removed_left, removed_right = removed.split(zeros[0])
            added_above_left, added_above_right = added_above.split(zeros[0])
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


class Min:

    def __init__(self):
        self.min = float('inf')
        self.values = []

    def add(self, interval: Interval):
        new_values = interval.get_extreme_value()
        self.values.append(new_values[0])
        self.values.append(new_values[1])
        self.min = min(self.min, min(new_values))

    def move(self, removed: Interval, added: Interval):
        other_minimum = min(self.values[2:])
        constant_interval = Interval(removed.start, removed.end, Polynomial.constant(other_minimum))
        added_shifted = added.move_above(removed)
        min_intervals = []
        first_chunk_intervals = removed.min_interval(constant_interval)
        for interval in first_chunk_intervals:
            min_intervals.extend(interval.min_interval(added_shifted.project_onto(interval)))
        return min_intervals

    def move_old(self, removed: Interval, added: Interval):
        added_left, added_right = added.get_extreme_value()
        removed_left, removed_right = removed.get_extreme_value()
        if self.min < min(removed_left, removed_right) and self.min < min(added_left, added_right):
            self.values.pop(0)
            self.values.pop(0)
            self.values.append(added_left)
            self.values.append(added_right)
            self.min = min(self.min, min(added_left, added_right))
            return Interval(removed.start, removed.end, Polynomial.constant(self.min))
        if self.min == removed_left and removed_right < min(added_left, added_right):
            other_minimum = min(self.values[1:])
            self.values.pop(0)
            self.values.pop(0)
            self.values.append(added_left)
            self.values.append(added_right)
            self.min = min(self.values)
            if other_minimum == removed_right:
                return removed
            else:
                return removed.min_interval(Interval(removed.start, removed.end, Polynomial.constant(other_minimum)))

        if self.min == removed_left and removed_right > min(added_left, added_right):
            # TBD problem.
            self.values.pop(0)
            self.values.pop(0)
            self.values.append(added_left)
            self.values.append(added_right)
            self.min = min(self.values)
            return removed
        if self.min == removed_right and self.min < min(added_left, added_right):
            self.values.pop(0)
            self.values.pop(0)
            self.values.append(added_left)
            self.values.append(added_right)
            self.min = min(self.values)
            return Interval(removed.start, removed.end, Polynomial.constant(removed_right))
        if self.min > max(added_left, added_right):
            self.values.pop(0)
            self.values.pop(0)
            self.values.append(added_left)
            self.values.append(added_right)
            self.min = min(self.values)
            if added_left < added_right:
                return Interval(removed.start, removed.end, added.function)
            else:
                return Interval(removed.start, removed.end, Polynomial.constant(added_right))
        if (self.min < min(removed_left, removed_right) or self.min == removed_right) and min(added_left,
                                                                                              added_right) < self.min < max(
            added_left,
            added_right):
            zero = (Polynomial.constant(self.min) - added.function).zeros()[0]  # PASS
            if added_left < added_right:
                return Interval(removed.start, zero, added.function), Interval(zero, removed.end,
                                                                               Polynomial.constant(self.min))
            else:
                return Interval(removed.start, zero, Polynomial.constant(self.min)), Interval(zero, removed.end,
                                                                                              added.function)
        if self.min == removed_left and min(added_left, added_right) < self.min < max(added_left, added_right):
            pass
