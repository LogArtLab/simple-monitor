class Notifier:

    def __init__(self):
        self.observers = []

    def to(self, observer):
        self.observers.append(observer)

    def notify(self, time, value):
        for observer in self.observers:
            observer(time, value)


class UnaryNode(Notifier):

    def __init__(self, operator):
        super().__init__()
        self.left = None
        self.right = None
        self.operator = operator

    def receive(self, time, value):
        self.notify(time, self.operator(value))


class BinaryNode(Notifier):

    def __init__(self, operator):
        super().__init__()
        self.left = None
        self.right = None
        self.operator = operator

    def receive_left(self, time, value):
        self.left = [time, value]
        if self.right:
            self.right[0] = time
            self.notify(time, self.operator(value, self.right[1]))

    def receive_right(self, time, value):
        self.right = [time, value]
        if self.left:
            self.left[0] = time
            self.notify(time, self.operator(value, self.left[1]))


class WindowObserver:
    def step(self, event_name, delta_time, value):
        pass

    def end(self, time):
        pass


class WindowNotifier:
    def __init__(self):
        self.observers = []

    def to(self, observer: WindowObserver):
        self.observers.append(observer)

    def notify_computation_step(self, event_name, delta_time, value):
        for observer in self.observers:
            observer.step(event_name, delta_time, value)

    def notify_computation_end(self, time):
        for observer in self.observers:
            observer.end(time)


class Window(WindowNotifier):

    def __init__(self, length):
        super().__init__()
        self.times = []
        self.values = []
        self.length = length
        self.accepting = True

    def add(self, time, value):
        if not self.accept(time, value):
            while self.move():
                continue

    def accept(self, time, value):
        if not self.times:
            self.times.append(time)
            self.values.append(value)
            return True
        elif time < self.times[0] + self.length:
            self.notify_computation_step("added", time - self.times[-1], self.values[-1])
            self.times.append(time)
            self.values.append(value)
            return True
        self.times.append(time)
        self.values.append(value)
        if self.accepting:
            missing_shift = self.times[0] + self.length - self.times[-2]
            self.notify_computation_step("added", missing_shift, self.values[-2])
            self.notify_computation_end(self.times[0])
            self.accepting = False
        return False

    def move(self):
        shift = self.times[-1] - (self.times[0] + self.length)
        if shift == 0:
            return False
        if shift < self.times[1] - self.times[0]:
            self.notify_computation_step("added", shift, self.values[-2])
            self.notify_computation_step("removed", shift, self.values[0])
            self.times[0] += shift
            self.notify_computation_end(self.times[0])
            return False
        elif shift == self.times[1] - self.times[0]:
            self.notify_computation_step("added", shift, self.values[-2])
            self.notify_computation_step("removed", shift, self.values[0])
            self.times.pop(0)
            self.values.pop(0)
            self.notify_computation_end(self.times[0])
            return False
        else:
            self.notify_computation_step("added", self.times[1] - self.times[0], self.values[-2])
            self.notify_computation_step("removed", self.times[1] - self.times[0], self.values[0])
            self.times.pop(0)
            self.values.pop(0)
            self.notify_computation_end(self.times[0])
            return True


class Reducer:

    def __init__(self, value, aggregator, function=lambda x: x):
        self.value = value
        self.aggregator = aggregator
        self.function = function

    def get_value(self):
        return self.value

    def add(self, element):
        self.value = self.aggregator(self.value, self.function(element))

    def remove(self, element):
        self.value = self.aggregator(self.value, -self.function(element))


class TemporalReducerNode(Notifier, WindowObserver):
    def __init__(self, window, reducer):
        super().__init__()
        self.window = window
        self.window.to(self)
        self.reducer = reducer

    def step(self, event, delta_time, value):
        if event == "removed":
            self.reducer.remove((delta_time, value))
        elif event == "added":
            self.reducer.add((delta_time, value))

    def end(self, time):
        self.notify(time, self.reducer.get_value())

    def receive(self, time, value):
        self.window.add(time, value)


class ShiftNode(Notifier):
    def __init__(self, time_delta):
        super().__init__()
        self.time_delta = time_delta
        self.firing_time = None
        self.firing_value = None
        self.times = []

    def receive(self, time, value):
        if self.firing_time is None:
            self.firing_time = time
            self.firing_value = value
        elif time <= self.firing_time + self.time_delta:
            self.firing_value = value
            self.times.append(time)
        else:
            self.notify(self.firing_time, self.firing_value)
            shift = time - (self.firing_time + self.time_delta)
            while self.firing_time + shift > self.times[0] and not self.times:
                self.times.pop(0)
            self.firing_time = self.firing_time + shift
            self.firing_value = value
            self.times.append(time)


class SpatialReducerNode(Notifier):

    def __init__(self, reducer):
        super().__init__()
        self.reducer = reducer
        self.storage = dict()

    def add(self, location_node, from_variable):
        variable_value = location_node.get_value(from_variable)
        if variable_value is not None:
            self.reducer.add(variable_value)
        self.storage[location_node.get_name()] = variable_value
        location_node.memory.add_observer(from_variable, lambda time, value: self.receive(time,
                                                                                          location_node.get_name(),
                                                                                          value))

    def receive(self, time, location_name, value):
        if self.storage[location_name] is None:
            self.storage[location_name] = value
            self.reducer.add(value)
        else:
            self.reducer.remove(self.storage[location_name])
            self.reducer.add(value)
            self.storage[location_name] = value
        if self.__should_notify():
            self.notify(time, self.reducer.get_value())

    def __should_notify(self):
        return None not in self.storage.values()
