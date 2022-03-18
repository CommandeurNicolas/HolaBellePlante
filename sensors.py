import sys

from grove.adc import ADC
from grove.button import Button
from grove.factory import Factory
from seeed_dht import DHT

class GroveMoistureSensor:
    '''
    Grove Moisture Sensor class
 
    Args:
        pin(int): number of analog pin/channel the sensor connected.
    '''
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()
 
    @property
    def moisture(self):
        '''
        Get the moisture strength value/voltage
 
        Returns:
            (int): voltage, in mV
        '''
        value = self.adc.read_voltage(self.channel)
        return value
    
class GroveLightSensor:
 
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()
 
    @property
    def light(self):
        value = self.adc.read(self.channel)
        return value
 
class GroveLedButton(object):
    def __init__(self, pin):
        self.counter = 0
        self.showFact = False
        
        # High = light on
        self.__led = Factory.getOneLed("GPIO-HIGH", pin)
        # Low = pressed
        self.__btn = Factory.getButton("GPIO-LOW", pin + 1)
        self.__on_event = None
        self.__btn.on_event(self, GroveLedButton.__handle_event)
 
    @property
    def on_event(self):
        return self.__on_event
 
    @on_event.setter
    def on_event(self, callback):
        if not callable(callback):
            return
        self.__on_event = callback
 
    def __handle_event(self, evt):
        # print("event index:{} event:{} pressed:{}".format(evt['index'], evt['code'], evt['presesed']))
        if callable(self.__on_event):
            self.__on_event(evt['index'], evt['code'], evt['time'])
            return
 
        self.__led.brightness = self.__led.MAX_BRIGHT
        event = evt['code']
        
        if event & Button.EV_SINGLE_CLICK:
            self.counter = (self.counter + 1) % 4
            self.__led.light(True)
            self.showFact = False
        #elif event & Button.EV_DOUBLE_CLICK:
        #    self.__led.blink()
        #    print("blink    LED")
        elif event & Button.EV_LONG_PRESS:
            self.__led.light(False)
            sys.exit()
            print("turn off LED and Exit")
        
class GroveTempMoistSensor():
    def __init__(self, channel):
        self.channel = channel
        self.dht = DHT("11", channel)
        
    def humiAndTemp(self):
        humi, temp = self.dht.read()
        return humi, temp
    
    def temp(self):
        humi, temp = self.dht.read()
        return temp
    
    def moisture(self):
        humi, temp = self.dht.read()
        return humi