# coding: utf-8
#-----------------------------------------------------------------------------------------
# BS440 plugin BS440csv.py
# About:
# Appends data to local CSV file
#
#
# Author: Specify the owner and contact details. Plugins will not be maintained by the
# developer of BS440.py unless specified otherwise.
#
#
#------------------------------------------------------------------------------------------
import logging
import csv

class Plugin:

    def __init__(self):
        return

    def execute(globalconfig, persondata, weightdata, bodydata):
        log = logging.getLogger(__name__)
        config = SafeConfigParser()
        config.read(__name__ + '.ini')
        personsection = 'Person' + str(persondata[0]['person'])
        if config.has_section(personsection):
            personname = config.get(personsection, 'username')
            csvFile = config.get(personsection, 'csvfile')
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
            with open(csvFile, 'rb') as csvfile:
                weightreader = csv.reader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csvlist = list(weightreader)
            csvfile.close()

        except:
            log.error('Failed to read CSV ' + personname + '.')

        try:
            # write to csv
            with open(csvFile, 'ab') as csvfile:
                weightwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for i, e in reversed(list(enumerate(weightdata))):
                    if any(str(weightdata[i]['timestamp']) in s for s in csvlist):
                        pass
                    else:
                        weightwriter.writerow([str(weightdata[i]['timestamp']), str(weightdata[i]['weight']), str(bodydata[i]['fat']), str(bodydata[i]['muscle']), str(bodydata[i]['bone']), str(bodydata[i]['tbw']), str(bodydata[i]['kcal']), str(calculateddata[i]['bmi'])])
                log.info('CSV successfully updated for ' + personname + '.')
        except:
            log.error('Failed to write CSV for ' + personname + '.')
