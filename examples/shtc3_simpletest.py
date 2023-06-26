# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
from machine import Pin, I2C
from micropython_shtc3 import shtc3

i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
sht = shtc3.SHTC3(i2c)

while True:
    temperature, relative_humidity = sht.measurements
    print("Temperature: {:0.1f} C".format(temperature))
    print("Humidity: {:0.1f} %%".format(relative_humidity))
    print()
    time.sleep(0.5)
