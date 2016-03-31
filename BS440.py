from __future__ import print_function
import pygatt.backends
import logging
from ConfigParser import SafeConfigParser
import time
import subprocess
from struct import *
from binascii import hexlify
from BS440decode import *
from BS440mail import *
from BS440domoticz import *


def processIndication(handle, values):
    '''
    Indication handler
    receives indication and stores values into result Dict
    (see medisanaBLE for Dict definition)
    handle: byte
    value: bytearray
    '''
    if handle == 0x25:
        result = decodePerson(handle, values)
        if result not in persondata:
            log.info(str(result))
            persondata.append(result)
        else:
            log.info('Duplicate persondata record')
    elif handle == 0x1b:
        result = decodeWeight(handle, values)
        if result not in weightdata:
            log.info(str(result))
            weightdata.append(result)
        else:
            log.info('Duplicate weightdata record')
    elif handle == 0x1e:
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
            found = adapter.filtered_scan(devname)
            # wait for scale to wake up and connect to it
        except pygatt.exceptions.BLEError:
            adapter.reset()
    return


def connect_device(address):
    device_connected = False
    tries = 3
    device = None
    while not device_connected and tries > 0:
        try:
            device = adapter.connect(address, 5, 'random')
            device_connected = True
        except pygatt.exceptions.NotConnectedError:
            tries -= 1
    return device


def init_ble_mode():
    p = subprocess.Popen("sudo btmgmt le on", stdout=subprocess.PIPE,
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
config = SafeConfigParser()
config.read('BS440.ini')

# set up logging
numeric_level = getattr(logging,
                        config.get('Program', 'loglevel').upper(),
                        None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)
logging.basicConfig(level=numeric_level,
                    format='%(asctime)s %(levelname)-8s %(funcName)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=config.get('Program', 'logfile'),
                    filemode='w')
log = logging.getLogger(__name__)

ble_address = config.get('Scale', 'ble_address')
device_name = config.get('Scale', 'device_name')
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
        bytearray to handle 0x23. This will resync the scale's RTC.
        While waiting for a response notification, which will never
        arrive, the scale will emit 30 Indications on 0x1b and 0x1e each.
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
                    if config.has_section('Email'):
                        BS440mail(config, persondata, weightdatasorted, bodydatasorted)
                    if config.has_section('Domoticz'):
                        UpdateDomoticz(config, weightdatasorted)
                else:
                    log.error('Unreliable data received. Unable to process')
