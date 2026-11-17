from machine import Pin


class RotaryEncoder:
    # interrupts on CLK and find directions with DT

    def __init__(self, clk_pin, dt_pin):
        self.clk = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self.dt = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        self._count = 0
        self._last = 0
        self.clk.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.handler) # sets so it triggers on both edges

    # checks the value of CLK with DT to determine rotation
    def handler(self, pin):
        if self.clk.value() != self.dt.value():
            self._count += 1 #clockwise
        else:
            self._count -= 1 #anticlockwise

    def get_change(self):
        # returns the number of rotations since the last call
        count = self._count
        change = count - self._last
        self._last = count
        return change

    def deinit(self):
        self.clk.irq(handler=None)