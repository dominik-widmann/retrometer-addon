#!/usr/bin/env python
from smbus import SMBus
import time



class MMC5983MA:
    i2caddress = 0x30
    controlReg0 = 0x09
    controlReg2 = 0x0b
    statusReg = 0x08
    tempOutReg = 0x07
    Xout0Reg = 0x00
    Xout1Reg = 0x01
    Yout0Reg = 0x02
    Yout1Reg = 0x03
    Zout0Reg = 0x04
    Zout1Reg = 0x05
    XYZout2Reg = 0x06

    def __init__(self, i2c_bus):
        self._i2c_bus = i2c_bus
        self.setup_sensor()

    def read_magnetometer(self):
        '''
        Read the magnetometer values and return them as a tuple (x,y,z).
        '''
        xout0 = self._i2c_bus.read_byte_data(self.i2caddress, self.Xout0Reg)
        xout1 = self._i2c_bus.read_byte_data(self.i2caddress, self.Xout1Reg)
        xyzout2 = self._i2c_bus.read_byte_data(self.i2caddress, self.XYZout2Reg)
        
        yout0 = self._i2c_bus.read_byte_data(self.i2caddress, self.Yout0Reg)
        yout1 = self._i2c_bus.read_byte_data(self.i2caddress, self.Yout1Reg)
        
        zout0 = self._i2c_bus.read_byte_data(self.i2caddress, self.Zout0Reg)
        zout1 = self._i2c_bus.read_byte_data(self.i2caddress, self.Zout1Reg)
        
        x = ((xout0 << 10) + (xout1 << 2) + ((xyzout2 >> 6) & 0b00000011)) * 0.0625 - 8000.0
        y = ((yout0 << 10) + (yout1 << 2) + ((xyzout2 >> 4) & 0b00000011)) * 0.0625 - 8000.0
        z = ((zout0 << 10) + (zout1 << 2) + ((xyzout2 >> 2) & 0b00000011))* 0.0625 - 8000.0
        return (x,y,z)

    def read_temperature(self):
        '''
        Read the temperature sensor value.
        '''
        temp_raw = self._i2c_bus.read_byte_data(self.i2caddress, self.tempOutReg)
        temp = temp_raw*0.8 + (-75.0)
        return temp

    def setup_sensor(self):
        """
        Setup the sensor to automatically calibrate and to continuously output data
        """
        controlReg0Data = 0b00100110 # automatic set/reset
        self._i2c_bus.write_byte_data(self.i2caddress, self.controlReg0, controlReg0Data)
        controlReg2Data = 0b00001101 # no set reset 
        self._i2c_bus.write_byte_data(self.i2caddress, self.controlReg2, controlReg2Data) 
        time.sleep(1.0)

    def is_new_meas_available(self):
        status = self._i2c_bus.read_byte_data(self.i2caddress,self.statusReg)
        return status & 0b00000011
