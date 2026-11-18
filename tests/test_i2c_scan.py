"""
Stand-alone test of the shared I2C0 bus (SDA GP4, SCL GP5).

Expected devices:
    0x10  Si4703 FM tuner (only after the reset sequence below!)
    0x3C  OLED display

The Si4703 chooses its bus mode at reset: SDIO (= SDA, GP4) must be LOW
while RST goes HIGH to select the 2-wire (I2C) mode. Without this sequence
the tuner does not answer and the scan shows only the display.
"""

from machine import I2C, Pin
import time

SDA_PIN = 4
SCL_PIN = 5
RST_PIN = 15
I2C_FREQ = 400_000

EXPECTED = {
    0x10: "Si4703 FM tuner",
    0x3C: "OLED display",
}


def reset_tuner():
    """Reset the Si4703 into I2C (2-wire) mode."""
    rst = Pin(RST_PIN, Pin.OUT, value=0)
    sda = Pin(SDA_PIN, Pin.OUT, value=0)  # SDIO low during reset
    time.sleep_ms(1)
    rst.value(1)                          # rising edge latches bus mode
    time.sleep_ms(1)
    # I2C() below reconfigures GP4 back to the I2C function


def print_table(found):
    """Print an i2cdetect-style address table."""
    print("      " + " ".join(f".{c:x}" for c in range(16)))
    for row in range(8):
        cells = []
        for col in range(16):
            addr = row * 16 + col
            cells.append(f"{addr:02x}" if addr in found else "--")
        print(f"0x{row:x}.: " + " ".join(cells))


def main():
    reset_tuner()
    i2c = I2C(0, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=I2C_FREQ)
    print(f"Bus: {i2c}")

    found = i2c.scan()
    print_table(found)
    print(f"\n{len(found)} device(s) detected\n")

    ok = True
    for addr, name in EXPECTED.items():
        if addr in found:
            print(f"[ OK ] {addr:#04x}  {name}")
        else:
            print(f"[FAIL] {addr:#04x}  {name} not found")
            ok = False

    for addr in found:
        if addr not in EXPECTED:
            print(f"[INFO] {addr:#04x}  unexpected device")

    print("\nI2C test", "PASSED" if ok else "FAILED")


if __name__ == "__main__":
    main()
