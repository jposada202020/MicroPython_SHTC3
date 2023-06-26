# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`shtc3`
================================================================================

MicroPython Driver for the Sensirion SHTC3 Temperature and Humidity Sensor


* Author(s): Jose D. Montoya


"""
import time
import struct
from micropython import const

try:
    from typing import Tuple
except ImportError:
    pass


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/MicroPython_SHTC3.git"


_DEVICE_ID = const(0xEFC8).to_bytes(2, "big")
_SOFTRESET = const(0x805D).to_bytes(2, "big")


SLEEP = const(0xB098)
WAKEUP = const(0x3517)
operation_mode_values = (SLEEP, WAKEUP)

NORMAL = const(0x7866)
LOW_POWER = const(0x609C)
power_mode_values = (NORMAL, LOW_POWER)


class SHTC3:
    """Driver for the SHTC3 Sensor connected over I2C.

    :param ~machine.I2C i2c: The I2C bus the SHTC3 is connected to.
    :param int address: The I2C device address. Defaults to :const:`0x70`

    :raises RuntimeError: if the sensor is not found

    **Quickstart: Importing and using the device**

    Here is an example of using the :class:`SHTC3` class.
    First you will need to import the libraries to use the sensor

    .. code-block:: python

        from machine import Pin, I2C
        from micropython_shtc3 import shtc3

    Once this is done you can define your `machine.I2C` object and define your sensor object

    .. code-block:: python

        i2c = I2C(1, sda=Pin(2), scl=Pin(3))
        sht = shtc3.SHTC3(i2c)

    Now you have access to the attributes

    .. code-block:: python

        temperature, relative_humidity = sht.measurements

    """

    def __init__(self, i2c, address: int = 0x70) -> None:
        self._i2c = i2c
        self._address = address

        if self._get_device_id() != 0x87:
            raise RuntimeError("Failed to find SHTC3")

        self._time_operation = None
        self.operation_mode = WAKEUP
        self.power_mode = NORMAL

    @property
    def operation_mode(self) -> str:
        """
        Sensor operation_mode

        +--------------------------+--------------------+
        | Mode                     | Value              |
        +==========================+====================+
        | :py:const:`shtc3.SLEEP`  | :py:const:`0xB098` |
        +--------------------------+--------------------+
        | :py:const:`shtc3.WAKEUP` | :py:const:`0x3517` |
        +--------------------------+--------------------+
        """
        values = {SLEEP: "SLEEP", WAKEUP: "WAKEUP"}
        return values[self._operation_mode]

    @operation_mode.setter
    def operation_mode(self, value: int) -> None:
        if value not in operation_mode_values:
            raise ValueError("Value must be a valid operation_mode setting")
        self._operation_mode = value
        self._i2c.writeto(self._address, value.to_bytes(2, "big"), False)
        time.sleep(0.001)

    @property
    def power_mode(self) -> str:
        """
        Sensor power_mode

        +-----------------------------+--------------------+
        | Mode                        | Value              |
        +=============================+====================+
        | :py:const:`shtc3.NORMAL`    | :py:const:`0x7866` |
        +-----------------------------+--------------------+
        | :py:const:`shtc3.LOW_POWER` | :py:const:`0x609C` |
        +-----------------------------+--------------------+
        """
        values = {NORMAL: "NORMAL", LOW_POWER: "LOW_POWER"}
        return values[self._power_mode]

    @power_mode.setter
    def power_mode(self, value: int) -> None:
        if value not in power_mode_values:
            raise ValueError("Value must be a valid power_mode setting")
        self._power_mode = value
        self._i2c.writeto(self._address, value.to_bytes(2, "big"), False)
        time.sleep(0.001)
        if value == LOW_POWER:
            self._time_operation = 0.001
        else:
            self._time_operation = 0.013

    def _get_device_id(self):
        """
        Get the device ID
        """
        data = bytearray(3)
        self._i2c.writeto(self._address, _DEVICE_ID, False)
        time.sleep(0.001)
        self._i2c.readfrom_into(self._address, data, True)
        return data[1]

    @property
    def measurements(self) -> Tuple[float, float]:
        """
        Take sensor readings. Temperature and Relative Humidity
        """
        self.operation_mode = WAKEUP
        data = bytearray(6)
        self._i2c.writeto(self._address, self._power_mode.to_bytes(2, "big"), False)
        time.sleep(self._time_operation)
        self._i2c.readfrom_into(self._address, data, False)

        temp_data = data[0:2]
        temp_crc = data[2]
        humidity_data = data[3:5]
        humidity_crc = data[5]

        if temp_crc != self._crc8(temp_data) or humidity_crc != self._crc8(
            humidity_data
        ):
            raise RuntimeError("CRC Mismatched")

        raw_temp = struct.unpack_from(">H", temp_data)[0]
        raw_temp = ((4375 * raw_temp) >> 14) - 4500
        temperature = raw_temp / 100.0

        # repeat above steps for humidity data
        raw_humidity = struct.unpack_from(">H", humidity_data)[0]
        raw_humidity = (625 * raw_humidity) >> 12
        humidity = raw_humidity / 100.0

        self.operation_mode = SLEEP

        return temperature, humidity

    @staticmethod
    def _crc8(buffer: bytearray) -> int:
        """verify the crc8 checksum"""
        crc = 0xFF
        for byte in buffer:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = (crc << 1) ^ 0x31
                else:
                    crc = crc << 1
        return crc & 0xFF

    @property
    def relative_humidity(self) -> float:
        """The current relative humidity in % rH. This is a value from 0-100%."""
        return self.measurements[1]

    @property
    def temperature(self) -> float:
        """The current temperature in degrees Celsius"""
        return self.measurements[0]
