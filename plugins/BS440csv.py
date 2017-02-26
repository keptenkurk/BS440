# coding: utf-8
#-----------------------------------------------------------------------------------------
# BS440 plugin BS440csv.py
# About:
# Appends data to local CSV file
#
__author__ = 'DjZU'
__email__ = "djzu89@gmail.com"
__license__ = "EUPL-1.1"
__version__ = "1.0.1"
__status__ = "Production"
#
#------------------------------------------------------------------------------------------
import csv

class Plugin:

    def __init__(self):
	return

    def execute(globalconfig, persondata, weightdata, bodydata):
	log = logging.getLogger(__name__)
	personID = persondata[0]['person']
	csvFile = './BS440csv/' + str(personID) + '.csv'

	# calculate BMI data list
	calculateddata = []
	datetimedata = []
	size = persondata[0]['size'] / 100.00
	for i, e in list(enumerate(weightdata)):
	    bmiDict = {}
	    bmiDict['bmi'] = round(weightdata[i]['weight'] / (size * size), 1)
	    calculateddata.append(bmiDict)

	if os.path.isfile(csvFile):
		try:
		    # read CSV
		    with open(csvFile, 'rb') as csvfile:
			weightreader = csv.reader(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			csvlist = list(weightreader)

		except:
		    log.error('Failed to read CSV for person %d' % personID)

	try:
	    # update CSV
	    with open(csvFile, 'ab') as csvfile:
		weightwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for i, e in reversed(list(enumerate(weightdata))):
		    if any(str(weightdata[i]['timestamp']) in s for s in csvlist):
			pass
		    else:
			weightwriter.writerow([str(weightdata[i]['timestamp']), str(weightdata[i]['weight']), str(bodydata[i]['fat']), str(bodydata[i]['muscle']), str(bodydata[i]['bone']), str(bodydata[i]['tbw']), str(bodydata[i]['kcal']), str(calculateddata[i]['bmi'])])
		log.info('CSV successfully updated for person %d' % personID)
	except:
	    log.error('Failed to write CSV for person %d' % personID)
