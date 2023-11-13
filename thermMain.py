#main Pico code

from thermistorTemp import Thermistor
from SSD1306 import SSD1306_I2C
import framebuf
from machine import Pin, I2C
from accel import accelerometer
from time import sleep
import network, ubinascii
import requests
from secrets import Tufts_Wireless as wifi
from mqtt import MQTTClient


'''---set-up-connection-to-wifi-network---'''
#def connect_wifi(wifi):
station = network.WLAN(network.STA_IF)
station.active(True)
mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
print("MAC " + mac)

station.connect(wifi['ssid'], wifi['pass'])
while not station.isconnected():
    sleep(1)
print('Connection successful')
print(station.ifconfig())

#connect_wifi(wifi)

'''TOP SECRET'''
AirTOKEN = ""
AirID = ""
AdaFrtUSER = ""
AdaFrtKEY = ""
'''CLASSIFIED'''

'''---set-up-connection-to-Adafruit-Dashboard---'''
#From ME35 Notion Page: "https://www.notion.so/WiFi-and-RestAPI-8b095bd343284376aa2867daed61a598"

url = 'https://io.adafruit.com/api/v2/%s/feeds' % AdaFrtUSER
headers = {'X-AIO-Key': AdaFrtKEY,'Content-Type':'application/json'}
try:
    reply = requests.get(url, headers=headers)    
    if reply.status_code == 200:
        reply = reply.json() #a JSON array of info
        keys = [x['key'] for x in reply]
        groups = [x['group']['name'] for x in reply]
        names = [x['name'] for x in reply]
        values = [x['last_value'] for x in reply]
        ids = [x['id'] for x in reply]
        print("Adafruit Access Granted...")
    else:
        print(f"Request failed with status code: {reply.status_code}")
except Exception as e:
    print(f"An error occurred: {e}")


'''---Connect-PC-as-Dashboard-Client---'''
try:
    client = MQTTClient("DL_Pico", "io.adafruit.com", 1883, user=AdaFrtUSER, password=AdaFrtKEY, keepalive=60)
    client.connect()
    print("We are in! Hello MQTT Broker...")
    #client.set_callback(whenCalled)
except OSError as e:
    print('Failed')
    


"""-------init-thermistor----------"""
adcpin = 26
thermistor = Thermistor(adcpin)
"""--------------------------------"""

"""---------init-display------------"""
WIDTH =128 
HEIGHT= 64
i2c=I2C(0,scl=Pin(13),sda=Pin(12),freq=200000)
oled = SSD1306_I2C(WIDTH,HEIGHT,i2c)
"""---------------------------------"""

"""---------init-accelerometer------------"""
accel = accelerometer(1, 19, 18, 100000)

'''-----converts-BMF-to-bytearray--- doesn't work yet :('''
def bmf_to_bytearray(file_path):
# (Supposedly) takes a GIF (in BMF format) and creates bytearray w/ elements for each image

    try:
        with open(file_path, "tempMeter.bmp") as bmf_file:
            bmf_data = bmf_file.read()
            bmf_bytearray = bytearray(bmf_data)
            return bmf_bytearray
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

#bArray = bmf_to_bytearray("tempMeter.bmp")
#fb = framebuf.FrameBuffer(bArray,64,64, framebuf.GS4_HMSB)
'''----------------------------------'''

'''---updates-temp-reading-to-most-current---'''
def tempUpdate(tempVals):
    tempVals[0] = thermistor.ReadTemperature()[0]
    tempVals[1] = thermistor.ReadTemperature()[1]
    print(tempVals)
    displayUpdate(tempVals)
    return tempVals
    
'''---updates-display-on-SSD1306-i2c-device---'''
def displayUpdate(tempVals):
    oled.fill(0)
    oled.text("temp " + tempUnit[tempIndicator] + ": " + str(tempVals[tempIndicator]), 0, 20)
    oled.rotate(2)
    oled.show()
    '''for i in range (0,128): # realized scroll operation would cause HUUUUGE delays (w/o async) for all aspects of MQTT process
                oled.scroll(-1,0)
                oled.show()
                sleep(.02)'''
    '''for i in range(-64,128): #same note as above; this loop is meant to show an animation on the display
       oled.blit(fb,i,0)
       oled.show()'''

'''---initialize-values-to-track-publish-and-requests---'''
temps = [0,0]
tempUnit = ["Celc", "Fahr"]
tempIndicator = 0

'''----Airtable-Setup-----'''
def tempMode():
    url = "https://api.airtable.com/v0/appvKT35VLaa4hxIj/Color Table" 
    headers = {"Authorization": "Bearer " + AirTOKEN, "Content-Type":"application/json"}
    reply = requests.get(url, headers=headers)
    if reply.status_code == 200:
        print(reply.json())
        reply = reply.json() #json array of info
        readColor = reply['records'][0]['fields']['Color Measure'] #pulls value from 'Color Measure' column position 0
        print(readColor)
        if readColor == "Green": # check for Fahrenheit
            tInd = 1
            tempUnit = "Fahr"
        elif readColor == "Red": # default to Celcius (red)
            tInd = 0
            tempUnit = "Celc"
        return tInd

while True:
    tempUpdate(temps)
    print(temps)
    tempIndicator = tempMode()
    print(tempIndicator)
    client.publish("dlilly01/feeds/temp", str(temps[tempIndicator]))
    sleep(5)
    print(accel.read_g())
    client.publish("dlilly01/feeds/accel", str(accel.read_g()))
    
