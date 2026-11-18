"""
Stand-alone test of the OLED display (Display class).

1. checks that the display answers at 0x3C,
2. shows the test screens one after another,
3. sweeps the frequency and measures how long one screen update takes
   (evidence of testing: display update time / max refresh rate),
4. tests the error screen.

Copy ``src/drivers/`` to the Pico (folder ``drivers``) before running.
"""

from machine import I2C, Pin
import time

from drivers.display import Display

SDA_PIN = 4
SCL_PIN = 5
FREQ_MIN = 875
FREQ_MAX = 1080


def measure_update(display, freq_hz, steps=50):
    """Redraw the radio screen ``steps`` times and return avg time in ms."""
    total = 0
    worst = 0
    for i in range(steps):
        selected = FREQ_MIN + (i * 4) % (FREQ_MAX - FREQ_MIN)
        start = time.ticks_us()
        display.show_radio(selected, tuned=selected, rssi=i % 76,
                           stereo=bool(i % 2))
        took = time.ticks_diff(time.ticks_us(), start)
        total += took
        worst = max(worst, took)
    avg_ms = total / steps / 1000
    print(f"I2C {freq_hz // 1000:3d} kHz: avg {avg_ms:5.1f} ms, "
          f"worst {worst / 1000:5.1f} ms, max ~{1000 / avg_ms:4.0f} fps")
    return avg_ms


def main():
    i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=400_000)

    try:
        display = Display(i2c)
    except OSError as e:
        print(f"[FAIL] {e} - check VCC, GND, SDA=GP4, SCL=GP5")
        return
    print("[ OK ] display found")

    try:
        # 1) text screen
        display.show_message("FM radio", "display test", "I2C 0x3C")
        time.sleep(2)

        # 2) radio screens: confirmed / not confirmed / no tune
        display.show_radio(1025, tuned=1025, rssi=45, stereo=True, preset=1)
        time.sleep(2)
        display.show_radio(1063, tuned=1025, rssi=45, stereo=True)
        time.sleep(2)
        display.show_radio(875, tuned=None, rssi=None)
        time.sleep(2)

        # 3) update time at both bus speeds
        print("Measuring screen update time...")
        for f in (100_000, 400_000):
            display.oled.i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN),
                                   freq=f)
            measure_update(display, f)

        # 4) error screen
        display.show_error("Tuner not found at 0x10")
        time.sleep(2)

        # 5) live sweep until Ctrl+C
        print("Sweeping frequency; press Ctrl+C to stop.")
        freq = FREQ_MIN
        while True:
            display.show_radio(freq, tuned=freq, rssi=(freq * 7) % 76,
                               stereo=freq % 2 == 0)
            freq = FREQ_MIN if freq >= FREQ_MAX else freq + 1
            time.sleep_ms(200)  # 5 Hz, same as display_task

    except KeyboardInterrupt:
        print("\nProgram stopped. Exiting...")
    finally:
        display.off()


if __name__ == "__main__":
    main()
