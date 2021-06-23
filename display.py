from machine import Pin


class Display:
    instance = None

    def __init__(self):
        self.displayPins = {
            "a": Pin(32, Pin.OUT),
            "d": Pin(33, Pin.OUT),
            "e": Pin(25, Pin.OUT),
            "f": Pin(26, Pin.OUT),
            "g": Pin(27, Pin.OUT)
        }

        self.coolingPos = 0

        for _, pin in self.displayPins.items():
            pin.off()

    @classmethod
    def get_instance(cls):
        if not Display.instance:
            Display.instance = Display()
        return Display.instance

    def cooling(self):
        if self.coolingPos == 0:
            self.bar_up()
        elif self.coolingPos == 1:
            self.bar_mid()
        elif self.coolingPos == 2:
            self.bar_low()
        self.coolingPos = (self.coolingPos + 1) % 3

    def write(self, states):
        for digit, value in states.items():
            self.displayPins[digit].value(value)

    def F(self):
        self.write({"a": 1, "g": 1, "f": 1, "e": 1, "d": 0})

    def L(self):
        self.write({"a": 0, "g": 0, "f": 1, "e": 1, "d": 1})

    def bar_up(self):
        self.write({"a": 1, "g": 0, "f": 0, "e": 0, "d": 0})

    def bar_mid(self):
        self.write({"a": 0, "g": 1, "f": 0, "e": 0, "d": 0})

    def bar_low(self):
        self.write({"a": 0, "g": 0, "f": 0, "e": 0, "d": 1})

    def I(self):
        self.write({"a": 0, "g": 0, "f": 1, "e": 1, "d": 0})

    def off(self):
        self.write({"a": 0, "g": 0, "f": 0, "e": 0, "d": 0})
