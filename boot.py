import network
import esp
import webrepl
import gc
import utime
from ujson import loads, dumps
from main import main


def connection(network_name, network_password):
    attempts = 0
    station = network.WLAN(network.STA_IF)
    if not station.isconnected():
        print("Connecting to network...")
        station.active(True)
        station.connect(network_name, network_password)
        while not station.isconnected():
            print("Attempts: {}".format(attempts))
            attempts += 1
            utime.sleep(5)
            if attempts > 3:
                return False
    print('Network Config:', station.ifconfig())
    return True


esp.osdebug(None)

gc.collect()

ssid = 'JagerMachineV2'
password = 'p@ssw0rd'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)

while not ap.active():
    pass

print('Connection successful')
print(ap.ifconfig())

existing_config = False
try:
    f = open("config.json", "r")
    configs = f.read()
    j = loads(configs)
    print(j)
    f.close()
    con = connection(j['network_name'], j['network_password'])
    if con is True:
        existing_config = True
        print("Network connected")
    else:
        existing_config = False
        print("Incorrect network configuration")
except:
    print("No saved network")


webrepl.start()

gc.collect()

main(existing_config, j)
