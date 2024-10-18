from simplemonitor.mrl.elements import Interval, Integral, WindowInterval, Min, WindowOperator
from simplemonitor.mrl.functions import Polynomial
from simplemonitor.mrl.notifiers import IntervalNotifier


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


class WindowNode(IntervalNotifier):
    def __init__(self, window: WindowInterval, window_operator: WindowOperator):
        super().__init__()
        window.to(self)
        self.window = window
        self.window_operator = window_operator

    def add(self, interval: Interval):
        self.window_operator.add(interval)

    def move(self, removed: Interval, added: Interval):
        results = self.window_operator.move(removed, added)
        for result in results:
            self.notify(result)

    def receive(self, interval: Interval):
        self.window.add(interval)


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


class MinNode(IntervalNotifier):
    def __init__(self, window: WindowInterval):
        super().__init__()
        window.to(self)
        self.window = window
        self.min = Min()

    def add(self, interval: Interval):
        self.min.add(interval)

    def move(self, removed: Interval, added: Interval):
        results = self.min.move(removed, added)
        for result in results:
            self.notify(result)

    def receive(self, interval: Interval):
        self.window.add(interval)


class ShiftNode(IntervalNotifier):
    def __init__(self, delta: float):
        super().__init__()
        self.delta = delta

    def receive(self, interval: Interval):
        self.notify(interval.shift(self.delta))
