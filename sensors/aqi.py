"""this is the aqi sensor driver SEN0460 that I implemented by reaading the document"""
"""default sda pin: 0x19""" 
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
address = 0x19

# (concentration ug/m3, ISPU value) knots, linearly interpolated between neighbours
PM25_KNOTS = [(0, 0), (15.5, 50), (55.4, 100), (150.4, 200), (250.4, 300), (500, 500)]
PM10_KNOTS = [(0, 0), (50, 50),   (150, 100),  (350, 200),   (420, 300),   (500, 500)]


# sensor code:

def read_reg(bus, address, reg, length, retries=5):
    last = None
    for _ in range(retries):   
        try:
            return bus.read_i2c_block_data(address, reg, length) #
        except OSError as e:
            last = e
        try:
            #first write to the reg of device address, then read from that reg
            bus.i2c_rdwr(i2c_msg.write(address, [reg]))
            time.sleep(0.01)
            msg = bus.i2c_rdwr(i2c_msg.read(address,[reg]))
            return list(msg)
        except OSError as e:
            last = e
        time.sleep(0.05)
    raise last

def main():
    bus = SMBus(BUS) #SMBus()opens a specified i2c bus, and create an object for communication 
    version = read_reg(bus, 0x19, REG_VERSION, 1)[0]
    print(f"the version for the sensor is:{version}")

if __name__ == "__main__":
    main()