from struct import *
import sys
'''
Reads Medisana BS440 Scale hex Indication and decodes scale
values from hex data string
This class provides 3 functions:
decodePerson, decodeWeight, decodeBody
Each function receives the hex handle and bytevalues and
returns a dictionary with decoded data
'''


def decodePerson(handle, values):
    '''
    decodePerson
    handle: 0x25
    values[0] = 0x84
    Returns a dict for convenience:
        valid (True, False)
        person (1..9)
        gender (male|female)
        age (0..255 years)
        size (0..255 cm)
        activity (normal|high)
    '''
    data = unpack('BxBxBBBxB', bytes(values[0:9]))
    retDict = {}
    retDict["valid"] = (handle == 0x25 and data[0] == 0x84)
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
    Handle: 0x1b
    Byte[0] = 0x1d
    Returns:
        valid (True, False)
        weight (5,0 .. 180,0 kg)
        timestamp (unix timestamp date and time of measurement)
        person (1..9)
        note: in python 2.7 to force results to be floats,
        devide by float.
        '''
    data = unpack('<BHxxIxxxxB', bytes(values[0:14]))
    retDict = {}
    retDict["valid"] = (handle == 0x1b and data[0] == 0x1d)
    retDict["weight"] = data[1]/100.0
    if data[2] < sys.maxint:
        retDict["timestamp"] = data[2]
    else:
        retDict["timestamp"] = 0
    retDict["person"] = data[3]
    return retDict


def decodeBody(handle, values):
    '''
    decodeBody
    Handle: 0x1e
    Byte[0] = 0x6f
    Returns:
        valid (True, False)
        timestamp (unix timestamp date and time of measurement)
        person (1..9)
        kcal = (0..65025 Kcal)
        fat = (0..100,0 %)  percentage of body fat
        tbw = (0..100,0 %) percentage of water
        muscle = (0..100,0 %) percentage of muscle
        bone = (0..100,0) bone weight
        note: in python 2.7 to force results to be floats: devide by float.
    '''
    data = unpack('<BIBHHHHH', bytes(values[0:16]))
    retDict = {}
    retDict["valid"] = (handle == 0x1e and data[0] == 0x6f)
    if data[1] < sys.maxint:
        retDict["timestamp"] = data[1]
    else:
        retDict["timestamp"] = 0
    retDict["person"] = data[2]
    retDict["kcal"] = data[3]
    retDict["fat"] = (0x0fff & data[4])/10.0
    retDict["tbw"] = (0x0fff & data[5])/10.0
    retDict["muscle"] = (0x0fff & data[6])/10.0
    retDict["bone"] = (0x0fff & data[7])/10.0
    return retDict
