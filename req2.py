#!/usr/bin/env python
import ADC0832
import time
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import board
import adafruit_dht
import time
import dweepy
import configfile
import emailtemp
import emailhumid

dweetIO = "https://dweet.io/dweet/for/" #common url for all users (post) 
myThing = "currenkh2" #replace with you OWN thing name
   
# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D24, use_pulseio=False)

greenLightPin= 5 # light LED
redLightPin = 22 # temperature LED
orangeLightPin = 25 # humidity LED

#GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM) # Refers to pin by Broadcom SOC Channel

# light LED setup
GPIO.setup(greenLightPin, GPIO.OUT) # Set pin mode as output
GPIO.output(greenLightPin, GPIO.LOW) # Output high level(+3.3V) to turn off the led

# temperature LED setup
GPIO.setup(redLightPin, GPIO.OUT) # Set pin mode as output
GPIO.output(redLightPin, GPIO.LOW) # Output high level(+3.3V) to turn off the led

# humidity LED setup
GPIO.setup(orangeLightPin, GPIO.OUT) # Set pin mode as output
GPIO.output(orangeLightPin, GPIO.LOW) # Output high level(+3.3V) to turn off the led

lightlvl = configfile.lightlvl
temp = configfile.temp
humid = configfile.humid

def init():
    ADC0832.setup()


def loop():
    while True:
        res = ADC0832.getResult() - 80
        if res < 0:
            res = 0
        if res > 100:
            res = 100
            
        print('////////////////////')
        print('////////////////////')
                    
        # Lux level more than 50
        if res > configfile.lightlvl:
            print('----LIGHT LEVEL----')
            print('Lighting: High')
            GPIO.output(greenLightPin, GPIO.LOW) # led off
        
        # Lux level less than 50
        if res < configfile.lightlvl:
            print('----LIGHT LEVEL----')
            print('Lighting: Low')
            GPIO.output(greenLightPin, GPIO.HIGH) # led on
        
        
        try:
            # Print the values to the serial port
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity
                    
            print('----TEMPERATURE & HUMIDITY----')
            print('####################')
            
            if temperature_f > configfile.temp:
                GPIO.output(redLightPin, GPIO.HIGH) # led on
                print('***HIGH TEMP***')
                emailtemp.email()
            else:
                GPIO.output(redLightPin, GPIO.LOW) # led off
        
            if humidity > configfile.humid:
                GPIO.output(orangeLightPin, GPIO.HIGH) # led on
                print('***HIGH HUMIDITY***')
                emailhumid.email()
            else:
                GPIO.output(orangeLightPin, GPIO.LOW) # led off
            
            print('####################')
            print(
                "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                    temperature_f, temperature_c, humidity
                )
            )
            key1= "temperature_c"
            key2= "humidity"
            
            dweepy.dweet_for(myThing, {key1: str(temperature_c), key2: str(humidity)})
            time.sleep(10.0)
                

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(1.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error

    time.sleep(2.0)
    #GPIO.cleanup()

if __name__ == '__main__':
    init()
    try:
        loop()
    except KeyboardInterrupt: 
        ADC0832.destroy()
        print ('The end !')


