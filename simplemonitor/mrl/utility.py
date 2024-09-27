class BufferedObserver:

    def __init__(self, observer):
        self.observer = observer
        self.values = dict()

    def receive(self, location_name, variable, time, value):
        if (location_name, variable) in self.values:
            data = self.values[(location_name, variable)]
            if data["time"] != time:
                self.observer(location_name, variable, data["time"], data["value"])
                self.values[(location_name, variable)] = {"time": time, "value": value}
            else:
                self.values[(location_name, variable)]["value"] = value
        else:
            self.values[(location_name, variable)] = {"time": time, "value": value}