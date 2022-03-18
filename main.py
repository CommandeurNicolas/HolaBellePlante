from time import sleep
from sensors import GroveMoistureSensor, GroveLightSensor, GroveLedButton, GroveTempMoistSensor
from funFacts import fun_facts
import time,sys,random

# this device has two I2C addresses
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e

# Max char per line on LCD screen
MAX_CHAR_PER_LINE = 16
 
if sys.platform == 'uwp':
    import winrt_smbus as smbus
    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)
        
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)

# send command to display (no need for external use)    
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)
 
# set display text \n for second line(or auto wrap)     
def setText(text):
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == MAX_CHAR_PER_LINE:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

#Update the display without erasing the display
def setText_norefresh(text):
    textCommand(0x02) # return home
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    
#    rows = text.split("\n")
#    for i in range(len(rows)):
#        while len(rows[i]) < MAX_CHAR_PER_LINE: #clears the rest of the screen
#            rows[i] += ' '
    
#    text = ""
#    if len(rows) > 1:
#        for row in rows:
#            text = text + row + " "
#    else:
#        text = rows[0]
        
#    if len(text) < MAX_CHAR_PER_LINE:
#        while len(text) < MAX_CHAR_PER_LINE:
#            text += ' '
            
    for c in text:
        if c == '\n' or count == MAX_CHAR_PER_LINE:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))
        
def fillString(text, to_nb_char=MAX_CHAR_PER_LINE):
    if len(text) < to_nb_char:
        while len(text) < to_nb_char:
            text += ' '
    return text
        
def getMoistureString(m):
    result = "Level : "
    if 0 <= m and m < 300:
        result += 'Dry'
        setRGB(194,223,239)
    elif 300 <= m and m < 600:
        result += 'Moist'
        setRGB(117,193,234)
    else:
        result += 'Wet'
        setRGB(11,54,232)

    result = fillString(result)
    
    return result

def getLightString(l):
    result = "Level : "
    if 0 <= l and l < 300:
        result += "Sleeping"
        setRGB(100,100,0)
    elif 300 <= l and l < 620:
        result += "Is OK"
        setRGB(200,200,0)
    else:
        result += "Too much"
        setRGB(255,255,0)

    result = fillString(result)
    
    return result

def getTemperatureString(t):
    result = "Level : "
    if t < 5:
        result += "Freezing"
        setRGB(0,190,230)
    elif 5 <= t and t < 30:
        result += "Comfy"
        setRGB(20,150,85)
    else:
        result += "Burning"
        setRGB(255,0,0)

    result = fillString(result)
    
    return result
    
def getFactPrintedText(text):
    return fillString(text, to_nb_char=32)

def printFact(fact, button):
    for i in range(len(fact)+1-MAX_CHAR_PER_LINE):
        if not button.showFact:
            break
        else:
            last_index = i+MAX_CHAR_PER_LINE
            text = getFactPrintedText(fact[i:last_index])
            
            setText_norefresh(text)
            
            if (i >= len(fact)-MAX_CHAR_PER_LINE):
                sleep(2)
            else:
                sleep(0.2)

def main():
    counter = 0
    funFactShown = False
    moistureSensor = GroveMoistureSensor(0)
    lightSensor = GroveLightSensor(4)
    tempMoistSensor = GroveTempMoistSensor(5)
    button = GroveLedButton(12)
    
    while True:
        sleep(0.5)
        if button.counter == 0:
            button.showFact = False
            m = moistureSensor.moisture
            text = "Moisture : {0}".format(m)
            text = fillString(text)
            text += getMoistureString(m)
            
            setText_norefresh(text)
        elif button.counter == 1:
            button.showFact = False
            l = lightSensor.light
            text = "Light : {0}".format(l)
            text = fillString(text)
            text += getLightString(l)
            
            setText_norefresh(text)
        elif button.counter == 2:
            button.showFact = False
            t = tempMoistSensor.temp()
            text = "Temp : {0}".format(t)
            text = fillString(text)
            text += getTemperatureString(t)
            
            setText_norefresh(text)
        elif button.counter == 3:
            button.showFact = True
            while button.showFact:
                setRGB(0,0,0)
                fact = fun_facts[random.randint(0,len(fun_facts)-1)]
                printFact(fact, button)
    

if __name__ == "__main__":
    main()
    
    
