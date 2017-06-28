#!/usr/bin/env python
# coding: ascii

from __future__ import print_function
import pygatt.backends
import logging
from ConfigParser import SafeConfigParser
import time
import subprocess
from struct import *
from binascii import hexlify
import os
import sys

from BS440decode import *


def processIndication(handle, values):
    '''
    Indication handler
    receives indication and stores values into result Dict
    (see BS440decode.py for Dict definition)
    handle: byte
    value: bytearray
    '''
    if handle == person_handle:
        result = decodePerson(handle, values)
        if result not in persondata:
            log.info(str(result))
            persondata.append(result)
        else:
            log.info('Duplicate persondata record')
    elif handle == weight_handle:
        result = decodeWeight(handle, values)
        if result not in weightdata:
            log.info(str(result))
            weightdata.append(result)
        else:
            log.info('Duplicate weightdata record')
    elif handle == body_handle:
        result = decodeBody(handle, values)
        if result not in bodydata:
            log.info(str(result))
            bodydata.append(result)
        else:
            log.info('Duplicate bodydata record')
    else:
        log.debug('Unhandled Indication encountered')


def wait_for_device(devname):
    found = False
    while not found:
        try:
            # wait for scale to wake up and connect to it
            found = adapter.filtered_scan(devname)
        except pygatt.exceptions.BLEError:
            # reset adapter when (see issue #33)
            adapter.reset()
    return


def connect_device(address):
    device_connected = False
    tries = 3
    device = None
    while not device_connected and tries > 0:
        try:
            device = adapter.connect(address, timeout, pygatt_address_type)
            device_connected = True
        except pygatt.exceptions.NotConnectedError:
            tries -= 1
    return device


def init_ble_mode():
    p = subprocess.Popen("btmgmt le on", stdout=subprocess.PIPE,
                         shell=True)
    (output, err) = p.communicate()
    if not err:
        log.info(output)
        return True
    else:
        log.info(err)
        return False

'''
Main program loop
'''
programConfig = SafeConfigParser()
programConfig.read('BS440.ini')
path = "plugins/"
plugins = {}

# set up logging
numeric_level = getattr(logging,
                        programConfig.get('Program', 'loglevel').upper(),
                        None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)
logging.basicConfig(level=numeric_level,
                    format='%(asctime)s %(levelname)-8s %(funcName)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=programConfig.get('Program', 'logfile'),
                    filemode='a')
log = logging.getLogger(__name__)

# Search for plugins in subdir "plugins" with name BS440*.py
sys.path.insert(0, path)
for f in os.listdir(path):
    fname, ext = os.path.splitext(f)
    if ext == '.py' and fname.startswith('BS440'):
        mod = __import__(fname)
        plugins[fname] = mod.Plugin()
sys.path.pop(0)

# Retrieve user configuration
ble_address = programConfig.get('Scale', 'ble_address')
device_name = programConfig.get('Scale', 'device_name')
device_model = programConfig.get('Scale', 'device_model')
timeout = int(programConfig.get('Program', 'timeout'))

# Retrieve scale configuration in subdir "models"
scaleConfig = SafeConfigParser()
scaleConfig.read('models/' + str(device_model) + '.ini')
person_handle = int(scaleConfig.get('ScaleConfiguration', 'person_handle'), 16)
weight_handle = int(scaleConfig.get('ScaleConfiguration', 'weight_handle'), 16)
body_handle = int(scaleConfig.get('ScaleConfiguration', 'body_handle'), 16)
write_handle = int(scaleConfig.get('ScaleConfiguration', 'write_handle'), 16)
address_type = scaleConfig.get('ScaleConfiguration', 'address_type')
if str(address_type) == "random":
	pygatt_address_type = pygatt.BLEAddressType.random
elif str(address_type) == "public":
	pygatt_address_type = pygatt.BLEAddressType.public
else:
	log.debug('Address type should be either \'random\' or \'public\'. It was \'' + str(address_type) + '\'.')
	sys.exit()

'''
Start BLE comms and run that forever
'''
log.info('BS440 Started')
if not init_ble_mode():
    sys.exit()

adapter = pygatt.backends.GATTToolBackend()
adapter.start()

while True:
    wait_for_device(device_name)
    device = connect_device(ble_address)
    if device:
        persondata = []
        weightdata = []
        bodydata = []
        continue_comms = True
        '''
        subscribe to characteristics and have processIndication
        process the data received.
        '''
        try:
            device.subscribe('00008a22-0000-1000-8000-00805f9b34fb',
                             callback=processIndication,
                             indication=True)
            device.subscribe('00008a21-0000-1000-8000-00805f9b34fb',
                             callback=processIndication,
                             indication=True)
            device.subscribe('00008a82-0000-1000-8000-00805f9b34fb',
                             callback=processIndication,
                             indication=True)
        except pygatt.exceptions.NotConnectedError:
            continue_comms = False

        '''
        Send the unix timestamp in little endian order preceded by 02 as
        bytearray to write_handle (0x23 for BS440). This will resync the scale's RTC.
        While waiting for a response notification, which will never arrive, 
		the scale will emit 30 Indications on weight_handle (0x1b for BS440) 
		and body_handle (0x1e for BS440) each.
        '''
        if continue_comms:
            timestamp = bytearray(pack('<I', int(time.time())))
            timestamp.insert(0, 2)
            try:
                device.char_write_handle(0x23, timestamp,
                                         wait_for_response=True)
            except pygatt.exceptions.NotificationTimeout:
                pass
            except pygatt.exceptions.NotConnectedError:
                continue_comms = False
            if continue_comms:
                log.info('Waiting for notifications for another 30 seconds')
                time.sleep(30)
                device.disconnect()
                log.info('Done receiving data from scale')
                # process data if all received well
                if persondata and weightdata and bodydata:
                    # Sort scale output by timestamp to retrieve most recent three results
                    weightdatasorted = sorted(weightdata, key=lambda k: k['timestamp'], reverse=True)
                    bodydatasorted = sorted(bodydata, key=lambda k: k['timestamp'], reverse=True)
                    
                    # Run all plugins found
                    for plugin in plugins.values():
                        plugin.execute(programConfig, persondata, weightdatasorted, bodydatasorted)
                else:
					log.error('Unreliable data received. Unable to process')
	else:
		log.debug('Failed to connect to the scale with address ' + str(ble_address) + '.')
