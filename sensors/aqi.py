"""this is the aqi sensor driver SEN0460 that I implemented by reaading the document"""

import argparse 
import math
import sys
import time
from collections import deque

try:
    from smbus2 import SMBus, i2c_msg
except ImportError:
    SMBus = i2c_msg = None

BUS = 1         #IC2 bus number
REG_POWER = 0x01                                       # write 0x02 = wake, 0x01 = low power
REG_VERSION = 0x1D                  #version of the registor for the sensor, specified by the vendor.   
REG_ATM = {"pm1": 0x0B, "pm25": 0x0D, "pm10": 0x0F}  #three measurements's address returned from sensor


# (concentration ug/m3, ISPU value) knots, linearly interpolated between neighbours
PM25_KNOTS = [(0, 0), (15.5, 50), (55.4, 100), (150.4, 200), (250.4, 300), (500, 500)]
PM10_KNOTS = [(0, 0), (50, 50),   (150, 100),  (350, 200),   (420, 300),   (500, 500)]


# sensor code:

def read_reg()