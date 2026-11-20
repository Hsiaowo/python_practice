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

# (concentration ug/m3, ISPU value) knots, linearly interpolated between neighbours--> shows the corresponding ug/m3 concentration to ISPU value
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
        #fall back method, if the read_i2c_block_data works, then no need to execute the following:
        try:
            #first write to the reg of device address, then read from that reg
            bus.i2c_rdwr(i2c_msg.write(address, [reg]))
            time.sleep(0.01)
            msg = i2c_msg.read(address,length)
            bus.i2c_rdwr(msg) #rdwr(read or write) function writes value to Object msg
            return list(msg)
        except OSError as e:
            last = e
        time.sleep(0.05)
    raise last

def read_pm(bus, address, retries=5):
    """a raw value with bit15 set (0x8001) is invalid, """
    out = {}
    for name, reg in REG_ATM.items(): #use <a dictionary item>.items() to unpack each entries into a key and a value
        value = 0
        for _ in range (retries):
            high, low = read_reg(bus, address, reg, 2)
            value = (high << 8) | low
            if not value & 0x8000: #if the value has bit 15 set(1000 0000 0000), then it would output a non-zero value
                out[name] = value
                break
                time.sleep(0.1)
        else:
            raise ValueError(f"the data at {name} is not working, (raw 0x:{ value})")
    return out
    
    
'''to calculating the air quality index in indonesia, we use ISPU index.to find what a concentration of ug/m3 data correspond to the index, 
we use interpolation'''
def sub_index(c, knots):
    if c is None or c <=0: 
        return 0
    for(x0, y0), (x1, y1) in zip(knots, knots[1:]):
        # use interpolating formula: x:concentration, y: corresponding index
        if c < x1:
            return y0 + (c - x0)/ (x1 - x0) * (y1 - y0) 
    return 500

def category(v): 
    if v <= 50 : return "good"
    if v <= 100 : return "moderate"
    if v <= 200 : return "unhealthy"
    if v <= 300 : return "very unhealthy"
    return "hazardous"

class WindowsMean:
    '''the sensor can mean over the last window_s seconds, and then stored as ~1440 bucket averages. 
    , it can continuously calculate the average pm2.5 concentration over the past 24 hours without storing
    every individual sensor reading'''
    def __init__(self, window_s):
        if not math.isfinite(window_s) or window_s <= 0:
            raise ValueError("the average window time must be finite and larger than 0")
        self.window_s = window_s
        self.bucket_s = max(1.0, window_s / 1440)
        self.buckets = deque() #python library for double ended queue, enable us to perform popleft(), appendleft(), pop(), append() to insert values
        self.cur_t, self.cur_sum, self.cur_n = None, 0, 0 #cur_t: current timestamp; cur_sum: current sum of sensor data; cur_n: current number of data entries
        self.started = time.time()
        
        def add(self, value, now=None):
            now = time.time() if now is None else now
            if self.cur_t is None:
                self.cur_t = now
            if now - self.cur_t >= self.bucket_s: # if there is more time period have gone than bucket_s 
                self.buckets.append((self.cur_t, self.cur_sum/self.cur_n))# append the timestamp, current average reading to the end of the queue "bucket"
                self.cur_t, self.cur_sum, self.cur_n = None, 0, 0 # after append the bucket, we need a new batch of sensor data coming in and we need to get rid of the old data. 
            self.cur_sum += value
            self.cur_n += 1
            while self.buckets and now - self.buckets[0][0] > self.window_s: #self.buckets checks whether the deque is empty
                #buckets[0][0] access the first tuple's first element in buckets, which is the initial timestamp
                #remove the expired bucket
                self.buckets.popleft() # popleft() removes the expired bucket.
            
            def mean(self):
                vals = [m for _, m in self.buckets] # _,m : timestamp, current average
                if self.cur_n:
                    vals.append(self.cur_sum / self.cur_n)
                return sum(vals) / len(vals) if vals else None
                
        
            def coverage(self, now=None): # this function checks the percentage of time frame that we have been averaging
                now = time.time()if now is None else now
                return min(1.0, (now - self.started) / self.window_s)
                



def main():
    bus = SMBus(BUS) #SMBus()opens a specified i2c bus, and create an object for communication 
    version = read_reg(bus, 0x19, REG_VERSION, 1)[0] #one length means 1 byte--> 8 bits
    print(f"the version for the sensor is:{version}")
    raw_pm_value = read_pm(bus, 0x19)
    print(f" the raw pm value is { raw_pm_value}")
    pm_index_25 = sub_index(raw_pm_value["pm25"], PM25_KNOTS)
    print(f" the pm25 index is {pm_index_25}, the category of the quality is: {category(pm_index_25)}")
    windowmean_testing = WindowsMean(2)
if __name__ == "__main__":
    main()