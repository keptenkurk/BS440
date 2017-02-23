#-----------------------------------------------------------------------------------------
# BS440 test utility BS440test.py
# About:
# This utility can be used to debug plugins without the need to take of your shoes and
# socks and step on the scale just to find that typo in the plugin.
#
# Data is taken from BS440test.ini and the array of results will be filled.
# Like the scale 30 values will be returned, from now and back, one day each. Values are slightly
# randomized with +/- 5% variation aroud the values supplied in BS440test.ini
# After this the data is presented to all the plugins found.
#
# Author:   Keptenkurk
# Date:     22/2/17
#
#------------------------------------------------------------------------------------------
from __future__ import print_function
import logging
from ConfigParser import SafeConfigParser
import time
import subprocess
from struct import *
from binascii import hexlify
import os
import sys
import random
import math


def randomize_a_bit(value):
    # deviate from value by -5% .. +5% rouded to 1 decimal
    deviation = 9.5 + random.random()
    return math.ceil(float(value) * deviation) / 10.0

'''
Main program loop
'''
config = SafeConfigParser()
config.read('BS440test.ini')
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

# Search for plugins in subdir "plugins" with name BS440*.py
sys.path.insert(0, path)
for f in os.listdir(path):
    fname, ext = os.path.splitext(f)
    if ext == '.py' and fname.startswith('BS440'):
        mod = __import__(fname)
        plugins[fname] = mod.Plugin()
sys.path.pop(0)

log.info('BS440 test Started')

persondata = []
weightdata = []
bodydata = []

current_timestamp = int(time.time())

persondict = {}
persondict["valid"] = True
persondict["gender"] = config.get('Scaledata', 'gender')
persondict["person"] = config.get('Scaledata', 'person')
persondict["age"] = config.get('Scaledata', 'age')
persondict["size"] = float(config.get('Scaledata', 'size'))
persondict["activity"] = config.get('Scaledata', 'activity')
persondata.append(persondict)

for i in range (0,29):
    weightdict = {}
    weightdict["valid"] = True
    # generate weighings per day
    weightdict["timestamp"] = current_timestamp - i * 86400
    weightdict["person"] = config.get('Scaledata', 'person')
    weightdict["weight"] = randomize_a_bit(config.get('Scaledata', 'weight'))
    weightdata.append(weightdict)
    
    bodydict = {}
    bodydict["valid"] = True
    # generate bodydata per day
    bodydict["timestamp"] = current_timestamp - i * 86400
    bodydict["person"] = config.get('Scaledata', 'person')
    bodydict["kcal"] = int(randomize_a_bit(config.get('Scaledata', 'kcal')))
    bodydict["fat"] = randomize_a_bit(config.get('Scaledata', 'fat'))
    bodydict["tbw"] = randomize_a_bit(config.get('Scaledata', 'tbw'))
    bodydict["muscle"] = randomize_a_bit(config.get('Scaledata', 'muscle'))
    bodydict["bone"] = randomize_a_bit(config.get('Scaledata', 'bone'))
    bodydata.append(bodydict)

log.info('Done generating testdata')
    # process data if all received well
if persondata and weightdata and bodydata:
    # Sort scale output by timestamp to retrieve most recent three results
    weightdatasorted = sorted(weightdata, key=lambda k: k['timestamp'], reverse=True)
    bodydatasorted = sorted(bodydata, key=lambda k: k['timestamp'], reverse=True)
    
    # Run all plugins found
    for plugin in plugins.values():
        plugin.execute(config, persondata, weightdatasorted, bodydatasorted)
else:
    log.error('No valid testdata found. Unable to process')
