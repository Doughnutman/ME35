#PC Operation
import paho.mqtt.client as mqtt
import requests
from time import sleep


'''---initialize-key-token-username-values-for-Airtable-and-Adafruit---'''
#these values must remain hidden for security purposes

AirTOKEN = "patpid0u4zKgSSFLx.a1eb213d9be25990bc8954c37f2122c04fb8d93a934b741033ff1ac6154aaa2a"
AirID = "patpid0u4zKgSSFLx"
AdaFrtUSER = "dlilly01"
AdaFrtKEY = "aio_aPQT84YbDJr272PMLEmOmsTgAxTr"


'''---set-up-connection-to-Adafruit-Dashboard---'''
#From ME35 Notion Page: "https://www.notion.so/WiFi-and-RestAPI-8b095bd343284376aa2867daed61a598"

url = 'https://io.adafruit.com/api/v2/%s/feeds' % AdaFrtUSER
key = AdaFrtKEY
headers = {'X-AIO-Key':AdaFrtKEY,'Content-Type':'application/json'}
reply = requests.get(url,headers=headers)
if reply.status_code == 200:
    reply = reply.json() #a JSON array of info
    keys = [x['key'] for x in reply]
    groups = [x['group']['name'] for x in reply]
    names = [x['name'] for x in reply]
    values = [x['last_value'] for x in reply]
    ids = [x['id'] for x in reply]
    

'''---Connect-PC-as-Dashboard-Client---'''
client = mqtt.Client("DL_PC")
client.username_pw_set(AdaFrtUSER, AdaFrtKEY)
client.connect("io.adafruit.com", 1883, keepalive=600)

'''---initialize-values-to-track-publish-and-requests---'''
tempUnits = ["C", "F"]
tempIndicator = 0 # used to call location within 'tempUnits' list
readColor = "Red" # used to get color status (from Airtable)

while True:
    #Adapted from ME35 Notion Page: "https://www.notion.so/WiFi-and-RestAPI-8b095bd343284376aa2867daed61a598"
    url = "https://api.airtable.com/v0/appvKT35VLaa4hxIj/Color Table" #new url -- modified and re-shared Airtable
    headers = {"Authorization": "Bearer " + AirTOKEN, "Content-Type":"application/json"}
    reply = requests.get(url, headers=headers)
    if reply.status_code == 200:
        print(reply.json())
        reply = reply.json() #json array of info
        readColor = reply['records'][0]['fields']['Color Measure'] #pulls value from 'Color Measure' column position 0
        print(readColor)
        if readColor == "Green": # check for Fahrenheit
            tempIndicator = 1
        elif readColor == "Red": # default to Celcius (red)
            tempIndicator = 0
        client.publish("dlilly01/feeds/tempUnit", tempUnits[tempIndicator]) # feeds unit of measure to dashboard
    sleep(2)
    
client.loop_forever()
