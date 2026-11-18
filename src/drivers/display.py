"""
Display – OLED output for the FM radio receiver.

Wraps the SH1106 128x64 I2C OLED (XPF1116-07A module, CH1116/SH1106
compatible controller) and draws the radio screens. The I2C bus object is
created once in the application and shared with the Si4703 tuner.

Example
-------
.. code-block:: python

    from machine import I2C, Pin
    from drivers.display import Display

    i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=400_000)
    display = Display(i2c)
    display.show_radio(selected=1025, tuned=1025, rssi=38, stereo=True)

Frequencies are integers in units of 100 kHz (1025 = 102.5 MHz), the same
convention as ``tests/test_encoder.py``.
"""

import framebuf
import time

from drivers.sh1106 import SH1106_I2C

RSSI_MAX = 75  # Si4703 RSSI range is 0..75 dBuV


class Display:
    """SH1106 OLED display with screens for the FM radio.

    :param i2c: shared ``machine.I2C`` bus object.
    :param addr: 7-bit I2C address of the display (default ``0x3C``).
    :raises OSError: if no device answers at ``addr``.
    """

    WIDTH = 128
    HEIGHT = 64

    def __init__(self, i2c, addr=0x3C):
        if addr not in i2c.scan():
            raise OSError(f"Display not found at {addr:#04x}")
        self.addr = addr
        self.oled = SH1106_I2C(i2c, addr=addr)
        self.last_update_ms = 0  # duration of the last show(), for testing
        self.clear()

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------
    def clear(self):
        """Clear the screen."""
        self.oled.fill(0)
        self._show()

    def _show(self):
        """Send the frame buffer to the display and measure how long it took."""
        start = time.ticks_ms()
        self.oled.show()
        self.last_update_ms = time.ticks_diff(time.ticks_ms(), start)

    def _big_text(self, text, x, y, scale=3):
        """Draw ``text`` enlarged ``scale`` times (built-in font is 8x8 px)."""
        width = 8 * len(text)
        buf = bytearray(width)  # 8 px high, MONO_VLSB = 1 byte per column
        small = framebuf.FrameBuffer(buf, width, 8, framebuf.MONO_VLSB)
        small.text(text, 0, 0, 1)
        for sx in range(width):
            column = buf[sx]
            if not column:
                continue
            for sy in range(8):
                if column & (1 << sy):
                    self.oled.fill_rect(x + sx * scale, y + sy * scale,
                                        scale, scale, 1)

    def _bar(self, x, y, width, height, value, maximum):
        """Outline bar filled proportionally to ``value / maximum``."""
        value = max(0, min(value, maximum))
        self.oled.rect(x, y, width, height, 1)
        filled = (width - 2) * value // maximum
        if filled > 0:
            self.oled.fill_rect(x + 1, y + 1, filled, height - 2, 1)

    # ------------------------------------------------------------------
    # Screens
    # ------------------------------------------------------------------
    def show_radio(self, selected, tuned=None, rssi=None, stereo=False,
                   preset=None):
        """Draw the main radio screen.

        :param selected: frequency chosen with the encoder (x100 kHz).
        :param tuned: frequency the tuner is actually on, or ``None``.
        :param rssi: received signal strength 0..75 dBuV, or ``None``.
        :param stereo: ``True`` if the tuner reports a stereo signal.
        :param preset: preset number to show, or ``None``.
        """
        o = self.oled
        o.fill(0)

        # Header: title, preset, stereo/mono
        o.text("FM", 0, 0)
        if preset is not None:
            o.text(f"P{preset}", 40, 0)
        o.text("ST" if stereo else "MO", 112, 0)
        o.hline(0, 10, self.WIDTH, 1)

        # Big frequency, right-aligned (3x scale = 24 px per character)
        freq_text = f"{selected // 10}.{selected % 10}"
        x = self.WIDTH - 24 * len(freq_text)
        self._big_text(freq_text, x, 14, scale=3)

        # Line under the frequency: confirmation state + unit
        if tuned is None:
            o.text("no tune", 0, 41)
        elif tuned != selected:
            o.text("touch=OK", 0, 41)  # selected but not yet confirmed
        o.text("MHz", 104, 41)

        # Signal strength
        o.text("RSSI", 0, 55)
        if rssi is None:
            o.text("--", 40, 55)
        else:
            self._bar(36, 55, 92, 8, rssi, RSSI_MAX)

        self._show()

    def show_message(self, line1, line2="", line3=""):
        """Show up to three lines of text (max 16 characters each)."""
        o = self.oled
        o.fill(0)
        o.text(line1, 0, 8)
        o.text(line2, 0, 28)
        o.text(line3, 0, 48)
        self._show()

    def show_error(self, message):
        """Show an error screen, e.g. when the tuner is missing."""
        o = self.oled
        o.fill(0)
        o.fill_rect(0, 0, self.WIDTH, 12, 1)
        o.text("ERROR", 44, 2, 0)
        o.text(message[:16], 0, 24)
        o.text(message[16:32], 0, 36)
        self._show()

    def contrast(self, value):
        """Set display contrast 0..255."""
        self.oled.contrast(value)

    def off(self):
        """Clear and switch the panel off."""
        self.oled.fill(0)
        self.oled.show()
        self.oled.poweroff()
