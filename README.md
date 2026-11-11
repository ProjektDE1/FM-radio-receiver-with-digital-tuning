# FM-radio-receiver-with-digital-tuning

# Team Members:

- Pažítka Samuel
- Pupík Milan
- Řihák Petr

# Overview

# Component list

- Raspberry Pi Pico 2 W
- Pico Gravity Board V3.0
- HW-763 Touch sensor
- HW-322 I2C FM tuner module, headphone jack
- Rotary encoder
- XPF1116-07A Y Display

# Block Diagram


# Pin/Bus Plan
------------------------------------
HW-763 Touch sensor
- I/O - GP2
- Ground
------------------------------------
HW-322 I2C FM tuner module, headphone jack
- RST - GP 15
- SDIO - D/4
- SCLK - C/5
- SEN - 3V3
- Ground
------------------------------------
Rotary encoder
- Ground
- SW - GP3
- CLK - C/5
- DT - D/4
------------------------------------
XPF1116-07A Y Display
- VCC - 3V3
- SCK - D/4
- SDA - C/5
- Ground
------------------------------------
LED 
- R - GP12
- G - GP13
- B - GP14
- Ground
------------------------------------
