from drivers.touch_sensor import TouchSensor
import time

TOUCH_PIN = 2

def main():
    touch = TouchSensor(TOUCH_PIN)
    events = 0

    print("Tap or hold the sensor; press Ctrl+C to stop.")

    try:
        while True:
            event = touch.update()

            if event == "short":
                events += 1
                print(f"{time.ticks_ms()} Short touch: confirm (#{events})")

            elif event == "long":
                events += 1
                print(f"{time.ticks_ms()} Long touch: save preset (#{events})")

            time.sleep_ms(20)

    except KeyboardInterrupt:
        print(f"\nProgram stopped. Exiting... ({events} events)")


if __name__ == "__main__":
    main()