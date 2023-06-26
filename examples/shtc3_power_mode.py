# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
from machine import Pin, I2C
from micropython_shtc3 import shtc3

i2c = I2C(1, sda=Pin(2), scl=Pin(3))  # Correct I2C pins for RP2040
sht = shtc3.SHTC3(i2c)

sht.power_mode = shtc3.NORMAL

# After running this example you might need to power-off and on
# the sensor. If you try to use the sensor afterward you might get
# and EIO error

while True:
    for power_mode in shtc3.power_mode_values:
        print("Current Operation mode setting: ", sht.power_mode)
        for _ in range(10):
            temp = sht.temperature
            print("Temperature: {:.2f}C".format(temp))
            print()
            time.sleep(0.5)
        sht.power_mode = power_mode
