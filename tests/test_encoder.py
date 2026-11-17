from drivers.rotary_encoder import RotaryEncoder
import time

#starting parameters; freq in MHz

CLK_PIN = 10
DT_PIN = 11
FREQ_MIN = 875     
FREQ_MAX = 1080     


def main():
    encoder = RotaryEncoder(CLK_PIN, DT_PIN)
    freq = FREQ_MIN
    total = 0

    print("Turn the encoder; press Ctrl+C to stop.")

    try:
        while True:
            change = encoder.get_change()
            if change:
                total += change
                freq = max(FREQ_MIN, min(FREQ_MAX, freq + change))
                print(
                    f"\rFrequency: {freq / 10:5.1f} MHz  "
                    f"delta: {change:+d}  total: {total:+4d}  ", end=""
                )

            time.sleep_ms(20)

    except KeyboardInterrupt:
        print("\nProgram stopped. Exiting...")
        encoder.deinit()


if __name__ == "__main__":
    main()