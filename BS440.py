from __future__ import print_function
import pygatt.backends
import logging
from configparser import ConfigParser
import time
import subprocess
from struct import *
from binascii import hexlify
import os
import sys

# Relevant characteristics submitted by the scale
# (Explanation see below)
Char_person = '00008a82-0000-1000-8000-00805f9b34fb'  # person data
Char_weight = '00008a21-0000-1000-8000-00805f9b34fb'  # weight data
Char_body = '00008a22-0000-1000-8000-00805f9b34fb'  # body data
Char_command = '00008a81-0000-1000-8000-00805f9b34fb'  # command register

'''
Information on the functions decodePerson, decodeWeight, decodeBody

The scale submits relevant data by use of Indications.
Indications are messages conveying the data for certain characteristics.
Characteristics have a two-byte shortcut for it (the handle) an a 16 byte
(globally unique) identifier (the UUID).

Relevant characteristics:
Description Handle      UUID                                  Data
            (2 byte)    (16 byte, globally unique)
Person      0x26        00008a82-0000-1000-8000-00805f9b34fb  person, gender, age, size, activity
Weight      0x1c        00008a21-0000-1000-8000-00805f9b34fb  weight, time, person
Body        0x1f        00008a22-0000-1000-8000-00805f9b34fb  time, person, kcal, fat, tbw, muscle, bone 

Writing the command 0200 to a handle tells the device that you register to the
indications of this characteristic. Writing 0000 will stop it.

A data packet of a characteristic (hex data string) will report with a
handle 1 less than the handle of the characteristic. E.g. writing 0200
to 0x26 (Person) will report back with the handle 0x25.

The last 30 measurements per person will be stored in the scale and upon
communication, the history for this user will be dumped. So you will
receive 30 values like this: 
handle=0x25, value=0x845302800134b6e0000000000000000000000000
handle=0x1b, value=0x1d8c1e00fe6e0aa056451100ff020900000000
handle=0x1e, value=0x6f6e0aa05602440ab8f07ff26bf11ef0000000

To decode the scale values (from hex data strings), three separate functions
are used. Each function receives the hex handle (e.g. 0x25) and bytevalues,
and then returns a dictionary with the decoded data. The datastrings are
interpreted using struct.unpack (see here https://docs.python.org/2/library/struct.html).
'''

def decodePerson(handle, values):
    '''
    decodePerson
    Handle: 0x25 (Person)                
    Value:
        Byte  Data                         Value/Return   Interpretation pattern
        0     fixed byte (validity check)  [0x84]         B (integer, lenght 1)
        1     -pad byte-                                  x (pad byte)
        2     person                       [1..8]         B ((integer, lenght 1)
        3     -pad byte-                                  x (pad byte)
        4     gender (1=male, 2=female)    [1|2]          B (integer, lenght 1)
        5     age                          [0..255 years] B (integer, lenght 1)
        6     size                         [0..255 cm]    B (integer, lenght 1)
        7     -pad byte-                                  x (pad byte)
        8     activity (0=normal, 3=high)  [0|3]          B (integer, lenght 1)
        --> Interpretation pattern:                       BxBxBBBxB
    '''
    data = unpack('BxBxBBBxB', bytes(values[0:9]))
    retDict = {}
    retDict["valid"] = (data[0] == 0x84)
    retDict["person"] = data[1]
    if data[2] == 1:
        retDict["gender"] = "male"
    else:
        retDict["gender"] = "female"
    retDict["age"] = data[3]
    retDict["size"] = data[4]
    if data[5] == 3:
        retDict["activity"] = "high"
    else:
        retDict["activity"] = "normal"
    return retDict


def decodeWeight(handle, values):
    '''
    decodeWeight
    Handle: 0x1b (Weight)             
    Value:
        Byte  Data                         Value/Return       Interpretation pattern
         0    fixed byte (validity check)  [0x1d]             B (integer, length 1)
         1    weight                       [5,0..180,0 kg]    H (integer, length 2)                     
         2    weight                       
         3    -pad byte-                                      x (pad byte)
         4    -pad byte-                                      x (pad byte)   
         5    timestamp                    Unix, date & time  I (integer, length 4)
         6    timestamp              
         7    timestamp                                 
         8    timestamp
         9    -pad byte-                                      x (pad byte) 
        10    -pad byte-                                      x (pad byte) 
        11    -pad byte-                                      x (pad byte) 
        12    -pad byte-                                      x (pad byte) 
        13    person                       [1..8]             B (integer, length 1)
        --> Interpretation pattern:                           BHxxIxxxxB              
    '''
    data = unpack('<BHxxIxxxxB', bytes(values[0:14]))
    retDict = {}
    retDict["valid"] = (data[0] == 0x1d)
    # Weight is reported in 10g. Hence, divide by 100.0
    # To force results to be floats: devide by float.
    retDict["weight"] = data[1]/100.0
    retDict["timestamp"] = sanitize_timestamp(data[2])
    retDict["person"] = data[3]
    return retDict


def decodeBody(handle, values):
    '''
    decodeBody
    Handle: 0x1e (Body)               
    Value:
        Byte  Data                          Value/Return       Interpretation pattern
         0    fixed byte (validity check)   [0x6f]             B (integer, lenght 1)
         1    timestamp                     Unix, date & time  I (integer, length 4)
         2    timestamp              
         3    timestamp                                 
         4    timestamp
         5    person                        [1..8]             B (integer, lenght 1)
         6    kcal                          [0..65025 Kcal]    H (integer, length 2)
         7    kcal
         8    fat (percentage of body fat)  [0..100,0 %]       H (integer, length 2)
         9    fat (percentage of body fat)
        10    tbw (percentage of water)     [0..100,0 %]       H (integer, length 2)
        11    tbw (percentage of water)
        12    muscle (percentage of muscle) [0..100,0 %]       H (integer, length 2)
        13    muscle (percentage of muscle)
        14    bone (bone weight)            [0..100,0 %]       H (integer, length 2)
        15    bone (bone weight)
        --> Interpretation pattern:                            BIBBHHHHH
    Notes: For kcal, fat, tbw, muscle, bone: First nibble = 0xf
    '''
    data = unpack('<BIBHHHHH', bytes(values[0:16]))
    retDict = {}
    retDict["valid"] = (data[0] == 0x6f)
    retDict["timestamp"] = sanitize_timestamp(data[1])
    retDict["person"] = data[2]
    retDict["kcal"] = data[3]
    # Fat, water, muscle and bone are reported in *10. Hence, divide by 10.0
    # To force results to be floats: devide by float.
    retDict["fat"] = (0x0fff & data[4])/10.0
    retDict["tbw"] = (0x0fff & data[5])/10.0
    retDict["muscle"] = (0x0fff & data[6])/10.0
    retDict["bone"] = (0x0fff & data[7])/10.0
    return retDict


def sanitize_timestamp(timestamp):
    '''
    timestamp: timestamp of measurement transmitted by the scale

    On some scales (e.g. BS410 and BS444, maybe others as well), time=0
    equals 1/1/2010. However, goal is to have unix-timestamps. Thus, the
    function converts the "scale-timestamp" to unix-timestamp by adding
    the time-offset (most scales: 1262304000 = 01.01.2010) to the timestamp.
    '''
    retTS = 0
    # Fail-safe: The timestamp will only be sanitized, if it will be
    # below below the maximum unix timestamp (2147483647). Otherwise the
    # non-sanitized timestamp will be taken.
    if timestamp + time_offset < sys.maxsize:
        retTS = timestamp + time_offset
    else:
        retTS = timestamp
    # If already the non-sanitized timestamp is above the maximum unix timestamp
    # 0 will be taken instead.
    if timestamp >= sys.maxsize:
        retTS = 0
    return retTS


def appendBmi(size, weightdata):
    '''
    appendBMI: Calculates the BMI (not calculated/ provided by the scale itself).

    size: size of the person (fixed), stored in the scale
    weightdata: list of weights of the previous x measurements
    '''
    size = size / 100.00
    for element in weightdata:
        '''
        Some scales (e.g. BS 444) identify the max. 8 users via a "weight approximation".
        If a new (or guest) user stands on the scale, the scale is not able to identify the user.
        As a result, no size for the user is stored in the scale, and thus not transmitted
        to the script. In these situations, the script stopped (division by zero). The following
        check aims at solving this problem (https://github.com/keptenkurk/BS440/issues/102)
        '''
        if size == 0:
            element['bmi'] = 0
        else:
            element['bmi'] = round(element['weight'] / (size * size), 1)


def processIndication(handle, values):
    '''
    Indication handler:
    Receives indication, decodes the information stored in the bytearray, and
    stores values into result Dict (see decodePerson, decodeWeight and decodeBody
    functions for Dict definition).
     
    handle: byte (e.g. 0x26 for person, 0x1c for weight or 0x1f for body)
    values: bytearray (e.g. 0x845302800134b6e0000000000000000000000000)
    '''
    if handle == handle_person:
        result = decodePerson(handle, values)
        if result not in persondata:
            log.info(str(result))
            persondata.append(result)
        else:
            log.info('Duplicate persondata record')
    elif handle == handle_weight:
        result = decodeWeight(handle, values)
        if result not in weightdata:
            log.info(str(result))
            weightdata.append(result)
        else:
            log.info('Duplicate weightdata record')
    elif handle == handle_body:
        result = decodeBody(handle, values)
        if result not in bodydata:
            log.info(str(result))
            bodydata.append(result)
        else:
            log.info('Duplicate bodydata record')
    else:
        log.debug('Unhandled Indication encountered')


def wait_for_device(devname):
    '''
    Reset adapter in case of pygatt exception error
    '''
    found = False
    while not found:
        try:
            # wait for scale to wake up and connect to it under the scale name (devname)
            found = adapter.filtered_scan(devname)
        except pygatt.exceptions.BLEError:
            # reset adapter when (see issue /keptenkurk/BS440/issues/33)
            adapter.reset()
    return


def connect_device(address):
    '''
    Connects to the scale defined by the MAC address (address).
    If successful, returns the instance of the BLEDevice. Otherwise NULL.
    '''
    device_connected = False
    tries = 3
    device = None
    while not device_connected and tries > 0:
        try:
            # address: MAC address of the scale
            # 8: ?
            # addresstype: ?
            device = adapter.connect(address, 8, addresstype)
            device_connected = True
        except pygatt.exceptions.NotConnectedError:
            tries -= 1
    return device


def init_ble_mode():
    '''
    Activates Bluetooth LE
    '''
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
# Read .ini file and set plugins-folder
config = ConfigParser()
config.read('BS440.ini')
path = "plugins/"
plugins = {}

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
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(numeric_level)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(funcName)s %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

# Load configured plugins
if config.has_option('Program', 'plugins'):
    config_plugins = config.get('Program', 'plugins').split(',')
    config_plugins = [plugin.strip(' ') for plugin in config_plugins]
    log.info('Configured plugins: %s' % ', '.join(config_plugins))

    sys.path.insert(0, path)
    for plugin in config_plugins:
        log.info('Loading plugin: %s' % plugin)
        mod = __import__(plugin)
        plugins[plugin] = mod.Plugin()
    log.info('All plugins loaded.')
else:
    log.info('No plugins configured.')
sys.path.pop(0)

# Load scale information from .ini-file
ble_address = config.get('Scale', 'ble_address')
device_name = config.get('Scale', 'device_name')
device_model = config.get('Scale', 'device_model')

# Set BLE address type and time offset, depending on scale model
if device_model == 'BS410':
    addresstype = pygatt.BLEAddressType.public
    # On BS410 time=0 equals 1/1/2010. 
    # time_offset is used to convert to unix standard
    time_offset = 1262304000
elif device_model == 'BS444':
    addresstype = pygatt.BLEAddressType.public
    # On BS444 time=0 equals 1/1/2010. 
    # time_offset is used to convert to unix standard
    time_offset = 1262304000
else:
    addresstype = pygatt.BLEAddressType.random
    time_offset = 0


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
    # If the device was connected successfully (the variable "device" has
    # been defined an contains the instance of the BLEDevice) the main loop runs
    if device:
        persondata = []
        weightdata = []
        bodydata = []
        try:
            # Get the two-byte shortcut (the handle)
            handle_person = device.get_handle(Char_person)
            handle_weight = device.get_handle(Char_weight)
            handle_body = device.get_handle(Char_body)
            handle_command = device.get_handle(Char_command)
            continue_comms = True
        except pygatt.exceptions.NotConnectedError:
            log.warning('Error getting handles')
            continue_comms = False

        log.info('Continue Comms: ' + str(continue_comms))
        if (not continue_comms): continue

        '''
        subscribe to characteristics and have processIndication
        process the data received.
        '''
        try:
            device.subscribe(Char_weight,
                             callback=processIndication,
                             indication=True)
            device.subscribe(Char_body,
                             callback=processIndication,
                             indication=True)
            device.subscribe(Char_person,
                             callback=processIndication,
                             indication=True)
        except pygatt.exceptions.NotConnectedError:
            continue_comms = False

        '''
        Send the unix timestamp in little endian order preceded by 02 as
        bytearray to handle 0x23. This will resync the scale's RTC.
        While waiting for a response notification, which will never
        arrive, the scale will emit 30 Indications on 0x1b (weight)
        and 0x1e (body) each.
        '''
        if continue_comms:
            timestamp = bytearray(pack('<I', int(time.time() - time_offset)))
            timestamp.insert(0, 2)
            try:
                device.char_write_handle(handle_command, timestamp,
                                         wait_for_response=True)
            except pygatt.exceptions.NotificationTimeout:
                pass
            except pygatt.exceptions.NotConnectedError:
                continue_comms = False
            if continue_comms:
                log.info('Waiting for notifications for another 30 seconds')
                time.sleep(30)
                try:
                    device.disconnect()
                except pygatt.exceptions.NotConnectedError:
                    log.info('Could not disconnect...')

                log.info('Done receiving data from scale')
                # process data if all received well
                if persondata and weightdata and bodydata:
                    # Sort scale output by timestamp to retrieve most recent three results
                    weightdatasorted = sorted(weightdata, key=lambda k: k['timestamp'], reverse=True)
                    appendBmi(persondata[0]['size'], weightdata)
                    bodydatasorted = sorted(bodydata, key=lambda k: k['timestamp'], reverse=True)
                    
                    # Run all plugins found
                    for plugin in plugins.values():
                        plugin.execute(config, persondata, weightdatasorted, bodydatasorted)
                else:
                    log.error('Unreliable data received. Unable to process')
