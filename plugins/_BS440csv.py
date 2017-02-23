# coding: utf-8
#-----------------------------------------------------------------------------------------
# BS440 plugin BS440csv.py
# About:
# Appends data to local CSV file
#
#
# Author: DjZU
#
#
#------------------------------------------------------------------------------------------
import logging
import csv
import os
from ConfigParser import SafeConfigParser

class Plugin:

    def __init__(self):
        return

    def execute(self, globalconfig, persondata, weightdata, bodydata):
        log = logging.getLogger(__name__)
        log.info('Starting plugin: ' + __name__)
        plugindir = os.path.dirname(os.path.realpath(__file__)) + '/'
        configfile = plugindir + __name__ + '.ini'
        pluginconfig = SafeConfigParser()
        pluginconfig.read(configfile)
        log.info('ini read from: ' + configfile)
        
        personsection = 'Person' + str(persondata[0]['person'])
        if pluginconfig.has_section(personsection):
            personname = pluginconfig.get(personsection, 'username')
            csvFile = pluginconfig.get(personsection, 'csvfile')
        else:
            log.error('Unable to write CSV: No details found in ini file '
                        'for person %d' % (persondata[0]['person']))
            return

        # calculate bmi data list
        calculateddata = []
        datetimedata = []
        size = persondata[0]['size'] / 100.00
        for i, e in list(enumerate(weightdata)):
            bmiDict = {}
            bmiDict['bmi'] = round(weightdata[i]['weight'] / (size * size), 1)
            calculateddata.append(bmiDict)

        try:
            # read csv
            with open(plugindir + csvFile, 'rb') as csvfile:
                weightreader = csv.reader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csvlist = list(weightreader)
            csvfile.close()

        except:
            log.error('Failed to read CSV ' + personname + '.')

        try:
            # write to csv
            with open(plugindir + csvFile, 'ab') as csvfile:
                weightwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for i, e in reversed(list(enumerate(weightdata))):
                    if any(str(weightdata[i]['timestamp']) in s for s in csvlist):
                        pass
                    else:
                        weightwriter.writerow([str(weightdata[i]['timestamp']), str(weightdata[i]['weight']), str(bodydata[i]['fat']), str(bodydata[i]['muscle']), str(bodydata[i]['bone']), str(bodydata[i]['tbw']), str(bodydata[i]['kcal']), str(calculateddata[i]['bmi'])])
                log.info('CSV successfully updated for ' + personname + '.')
        except:
            log.error('Failed to write CSV for ' + personname + '.')
