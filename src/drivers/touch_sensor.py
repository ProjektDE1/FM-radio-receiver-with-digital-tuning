from machine import Pin
import time

class TouchSensor:
    # touch sensor class, right now can differentiate between long and short touch (confirm, save station)

    def __init__(self, pin, long_ms=800):
        self.pin = Pin(pin, Pin.IN)
        self.long_ms = long_ms
        self.was_touched = False
        self.start_ms = 0
        self.long_reported = False

    def is_touched(self):
        # when touched returns 1
        return self.pin.value() == 1

    def update(self):
        # called periodicaly, returns either short or long touch based on time 
        now_ms = time.ticks_ms()
        touched = self.is_touched()
        event = None

        if touched and not self.was_touched:
            # finger just placed on the pad: start measuring
            self.start_ms = now_ms
            self.long_reported = False

        elif touched and not self.long_reported:
            # finds the time of the touch and finds long vs short
            if time.ticks_diff(now_ms, self.start_ms) >= self.long_ms:
                self.long_reported = True
                event = "long"

        elif not touched and self._was_touched and not self.long_reported:
            # touched stopped happening before long_time has passed 
            event = "short"

        self._was_touched = touched
        return event