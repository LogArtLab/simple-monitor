from old.elements import LocationStorage


class Notifier:

    def __init__(self):
        self.observers = []

    def to(self, observer):
        self.observers.append(observer)

    def notify(self, time, value):
        for observer in self.observers:
            observer(time, value)


class Interval:

    def __init__(self, left, right):
        self.left = left
        self.right = right


class VariableNode(Notifier):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def receive(self, memory: dict):
        value = memory[self.name]
        self.notify(memory['time'], value)


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


class UnaryNode(Notifier):

    def __init__(self, operator):
        super().__init__()
        self.left = None
        self.right = None
        self.operator = operator

    def receive(self, time, value):
        self.notify(time, self.operator(value))


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


class UpdateObserver:
    def update(self, data):
        pass


class SpatialReducerNode(Notifier, UpdateObserver):
    def __init__(self, reducer):
        super().__init__()
        self.time = None
        self.reducer = reducer
        self.storage = dict()

    def get_receiver(self, name):
        self.storage[name] = None
        return lambda time, value: self.update(name, time, value)

    def update(self, name, time, value):
        self.storage[name] = value
        if self.__should_notify():
            self.notify(self.time, self.reducer.get_value())
        self.time = time
        self.reducer.add(value)

    def __should_notify(self):
        return None not in self.storage.values()


class World:

    def __init__(self, locations):
        self.locations = locations

    def get_location_storage(self, relation):
        location_storage = LocationStorage(relation)
        for location in self.locations:
            location_storage.add_location(location)
        return location_storage


class GenericNotifier:

    def __init__(self):
        self.observers = []

    def to(self, observer):
        self.observers.append(observer)

    def notify(self, data):
        for observer in self.observers:
            observer(data)


class LocationDistanceStorage(GenericNotifier):

    def __init__(self, location_name, location_data, distance_function):
        super().__init__()
        self.location_name = location_name
        self.location_data = location_data
        self.distance_function = distance_function
        self.distance

    def update(self, location_name, data):
        if location_name != self.location_name & self.distance_function(self.location_data, data):
            pass


class LocationGrouper:

    def __init__(self):
        self.location_groups = dict()

    def update(self, data):
        self.loca


class Location(UpdateObserver):
    def __init__(self, location_name, world):
        super().__init__()
        self.location_name = location_name
        self.storage = dict()
        self.world = world
        self.world.to(self)
        self.location_value = dict()

    def update(self, data):
        pass

    def get_receiver(self, receiver_name):
        self.storage[receiver_name] = None
        return lambda time, value: self.receive(receiver_name, time, value)

    def receive(self, receiver_name, time, value):
        self.storage[receiver_name] = value
        self.world.notify(
            {"time": time, "location": self.location_name, "receiver_name": receiver_name, "value": value})
