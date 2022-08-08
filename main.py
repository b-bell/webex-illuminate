import requests
from retry import retry
from phue import Bridge
from time import sleep
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

webexOptions = config['webex']
myID = webexOptions['myID']
url = webexOptions['baseUrl'] + myID
token = webexOptions['token']

phueOptions = config['phue']
bridgeIpAddress = phueOptions['bridgeIpAddress']

@retry(tries=3, delay=3, backoff=2)
def getWebexStatus():
    headers = {
        'Authorization': 'Bearer ' + token
    }
    response = requests.request("GET", url, headers=headers)
    if (response.status_code == 200):
        responseJSON = response.json()
        return responseJSON['status']
    else:
        raise Exception('Max retries exceeded, unable to get Webex status: ' + response.reason)

def access_lights(bridgeIpAddress):
    b = Bridge(bridgeIpAddress)
    b.connect()
    light_names = b.get_light_objects('name')
    return light_names

def setLightOptions(status):
    lights = access_lights(bridgeIpAddress)
    try:
        lightOptions = config[status]
        for light in lights:
            lights[light].on = True
            lights[light].hue = int(lightOptions['hue'])
            lights[light].saturation = int(lightOptions['saturation'])
            lights[light].brightness = int(lightOptions['brightness'])
    except:
        for light in lights:
            lights[light].on = False      

def updateHueLight():
    currentStatus = ''
    while True:
        newStatus = getWebexStatus()
        if (currentStatus != newStatus):
            currentStatus = newStatus
            setLightOptions(currentStatus)
        sleep(1)

if __name__ == '__main__':
    updateHueLight()