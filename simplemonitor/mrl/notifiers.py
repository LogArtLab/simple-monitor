class IntervalNotifier:

    def __init__(self):
        self.observers = []

    def to(self, observer):
        self.observers.append(observer)

    def notify(self, interval):
        for observer in self.observers:
            observer(interval)


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
