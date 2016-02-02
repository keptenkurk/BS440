from __future__ import print_function
import pygatt.backends
import logging
import time
from struct import *
from binascii import hexlify
from medisanaBLE import *

def processIndication(handle, values):
    '''
    Indication handler
    receives indication and stores values into result Dict
    (see medisanaBLE for Dict definition)
    handle: byte
    value: bytearray
    TODO: check, is it possible that this takes too long?
    TODO: remove hexlify import if not required anymore
    '''
    if handle == 0x25:
        result = decodePerson(handle, values)
    elif handle == 0x1b:
        result = decodeWeight(handle, values)
    elif handle == 0x1e:
        result = decodeBody(handle, values)
    else:
        logging.DEBUG('Unhandled Indication encountered')
    print(result)  # Replace by storeData(result)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s [%(funcName)]s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='bs440.log',
                    filemode='w') 

BLE_ADDRESS = 'f1:37:57:xx:xx:xx'
    
'''
Start BLE comms and run that forever
'''
adapter = pygatt.backends.GATTToolBackend()
adapter.start()

while True:
    while True:  
        # wait for scale to wake up and connect to it
        try:
            device = adapter.connect(BLE_ADDRESS, 5, 'random')
            break
        except pygatt.exceptions.NotConnectedError:
            pass

    '''
    subscribe to characteristics and have processIndication 
    process the data received.
    '''
    device.subscribe('00008a22-0000-1000-8000-00805f9b34fb', 
                    callback = processIndication, indication=True)
    device.subscribe('00008a21-0000-1000-8000-00805f9b34fb', 
                    callback = processIndication, indication=True)
    device.subscribe('00008a82-0000-1000-8000-00805f9b34fb', 
                    callback = processIndication, indication=True)

    '''
    Send the unix timestamp in little endian order preceded by 02 as bytearray
    to handle 0x23. This will resync the scale's RTC.
    While waiting for a response notification, which will never arrive, 
    the scale will emit 30 Indications on 0x1b and 0x1e each.
    '''
    timestamp = bytearray(pack('<I', int(time.time())))
    timestamp.insert(0,2)
    try:
        device.char_write_handle(0x23, timestamp, wait_for_response=True)
    except pygatt.exceptions.NotificationTimeout:
        pass
    device.disconnect()
