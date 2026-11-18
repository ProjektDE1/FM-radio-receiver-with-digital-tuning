
from machine import Pin, I2C
import time

# -----------------------------
# PIN CONFIGURATION
# -----------------------------

SDA_PIN = 4       # Pico GP4 -> SI4703 D
SCL_PIN = 5       # Pico GP5 -> SI4703 C
RST_PIN = 15      # Pico GP15 -> SI4703 RST

SI4703_ADDR = 0x10

# -----------------------------
# RESET SI4703
# -----------------------------

print("\n==============================")
print("     SI4703 BENCH TEST")
print("==============================")

# SEN must be connected to 3V3
# Hold SDIO low during reset

sda = Pin(SDA_PIN, Pin.OUT)
scl = Pin(SCL_PIN, Pin.OUT)
rst = Pin(RST_PIN, Pin.OUT)

sda.value(0)
scl.value(1)
rst.value(0)

time.sleep_ms(10)

# Release reset while SDIO is LOW
rst.value(1)

time.sleep_ms(2)

# Release I2C lines
sda = Pin(SDA_PIN, Pin.OPEN_DRAIN)
scl = Pin(SCL_PIN, Pin.OPEN_DRAIN)

time.sleep_ms(10)

# -----------------------------
# INITIALIZE I2C
# -----------------------------

i2c = I2C(
    0,
    scl=Pin(SCL_PIN),
    sda=Pin(SDA_PIN),
    freq=100000
)

# -----------------------------
# I2C SCAN
# -----------------------------

print("\n[TEST 1] Scanning I2C bus...")

devices = i2c.scan()

for device in devices:
    print("Found device: 0x{:02X}".format(device))

if SI4703_ADDR not in devices:
    print("\nERROR: SI4703 NOT FOUND!")
    print("Check wiring, power and SEN/RST.")
    while True:
        time.sleep(1)

print("\nPASS: SI4703 detected at 0x10")

# -----------------------------
# READ SI4703 REGISTERS
# -----------------------------

def read_registers():

    # SI4703 reads start at register 0x0A
    data = i2c.readfrom(SI4703_ADDR, 32)

    registers = {}

    order = list(range(0x0A, 0x10)) + list(range(0x00, 0x0A))

    for i, reg in enumerate(order):
        registers[reg] = (
            (data[i * 2] << 8) |
            data[i * 2 + 1]
        )

    return registers

# -----------------------------
# IDENTIFICATION TEST
# -----------------------------

print("\n[TEST 2] Reading chip identification...")

time.sleep_ms(10)

try:

    regs = read_registers()

    device_id = regs[0x00]
    chip_id = regs[0x01]

    print("DEVICEID : 0x{:04X}".format(device_id))
    print("CHIPID   : 0x{:04X}".format(chip_id))

    if device_id in (0x0000, 0xFFFF):
        print("WARNING: Invalid DEVICEID")
    else:
        print("PASS: Device identification responded")

    if chip_id in (0x0000, 0xFFFF):
        print("WARNING: Invalid CHIPID")
    else:
        print("PASS: Chip identification responded")

except Exception as e:

    print("ERROR reading registers:", e)

# -----------------------------
# DISPLAY ALL REGISTERS
# -----------------------------

print("\n[TEST 3] Register dump")
print("------------------------------")

try:

    regs = read_registers()

    for reg in range(16):

        print(
            "REG 0x{:02X} = 0x{:04X}".format(
                reg, regs[reg]
            )
        )

    print("------------------------------")
    print("REGISTER READ TEST COMPLETE")

except Exception as e:

    print("REGISTER TEST FAILED:", e)

print("\n==============================")
print("      BENCH TEST FINISHED")
print("==============================")

while True:
    time.sleep(1)
