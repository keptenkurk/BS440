#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request, redirect, render_template, url_for
from ConfigParser import SafeConfigParser
import os

__author__ = 'DjZU'
__email__ = "djzu89@gmail.com"
__version__ = "1.0.1"
__status__ = "Production"

app = Flask(__name__)


# BS440 config
config = SafeConfigParser()
config.read('BS440.ini')
personsdata = []
persons = []
for section_name in config.sections():
	if config.has_option(section_name, 'username'):
		persons.append(config.get(section_name, 'username'))
		personsdata.append(persons)

# Flask
@app.route('/')

def index():

	return render_template('login.html', enumerate=enumerate, list=list, persons=persons)

@app.route('/<int:personID>')
def redirection_person_days(personID):

    return redirect('/' + str(personID) + '/' + '31')

@app.route('/<int:personID>/<int:days>')

def person(personID, days):
	personsection = 'Person' + str(personID)
	if config.has_section(personsection):
		person = config.get(personsection, 'username')
	else:
		print('Unable to plot: No details found in ini file '
		          'for person %d' % (int(personID)))
	dirname = os.path.dirname(__file__)
	plotTemplate = person.lower() + '-plot-' + str(days) + '.html'
	plotFile = './templates/' + plotTemplate
	plotPath = os.path.join(dirname, plotFile)
	csvFile = person.lower() + '.csv'
	csvPath = os.path.join(dirname, csvFile)
	# Update plot only is CSV contains new data
	if (os.path.isfile(csvPath) and os.path.isfile(plotPath) ):
		if (os.path.getmtime(csvPath) > os.path.getmtime(plotPath) ):
			os.system('python BS440plot.py -p ' + str(personID) + ' -w ' + str(days))
	elif (os.path.isfile(csvPath) ):
		os.system('python BS440plot.py -p ' + str(personID) + ' -w ' + str(days))

	return render_template('person.html', person=person, days=days, plotFile=plotTemplate)



if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5421, debug=True)

