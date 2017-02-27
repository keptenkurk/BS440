#!/usr/bin/env python
# coding: utf-8
#-----------------------------------------------------------------------------------------
# BS440 plugin BS440plot.py
# About:
# Generate charts from CSV file to HTML file whenever BS440flask.py requires it
#
# Requirements:
# BS440 plugin BS440csv.py
#
#
# Dependencies (install with 'sudo -H pip install packagename'):
# pandas math plotly scipy
#
__author__ = 'DjZU'
__email__ = "djzu89@gmail.com"
__license__ = "EUPL-1.1"
__version__ = "1.0.1"
__status__ = "Production"
#
#------------------------------------------------------------------------------------------
import pandas as pd
import plotly.graph_objs as go
import plotly.offline as plotly
import argparse
from datetime import datetime, timedelta
from ConfigParser import SafeConfigParser
from math import radians, cos, sin
from scipy import stats
import logging
import os
import sys

#-----------------------------------------------------------------------------------------
# Functions
#-----------------------------------------------------------------------------------------
def update_plotlyjs_for_offline():
	import urllib2
	cdn_url = 'https://cdn.plot.ly/plotly-latest.min.js'
	response = urllib2.urlopen(cdn_url)
	html = response.read()
	f = open('./static/plotly.min.js', 'w')
    	f.write(html)
	f.close()
	log.info('Done updating ./static/plotly.min.js')

# This code is shipped with version plotly.js v1.20.5 retrieved from /usr/local/lib/python2.7/dist-packages/plotly/package_data/plotly.min.js
# Uncomment to update ./static/plotly.min.js. Beware it could screw the display.
#update_plotlyjs_for_offline()

def convert_to_datetime(timestamp):
	if (timeWindow > 365):
		return datetime.fromtimestamp(int(timestamp)).strftime('%A%n%b %-d %Y%n%-H:%M')
	else:
		return datetime.fromtimestamp(int(timestamp)).strftime('%A%n%b %-d%n%-H:%M')

def prepare_weight_text(weight):
    return str(weight) + " kg"
def prepare_fat_text(fat):
    return "Fat:\t\t" + str(fat) + " %\n"
def prepare_muscle_text(muscle):
    return "Muscle:\t" + str(muscle) + " %\n"
def prepare_bone_text(bone):
    return "Bone:\t" + str(bone) + " kg\n"
def prepare_water_text(water):
    return "Water:\t" + str(water) + " %\n"
def prepare_bmi_text(bmi):
    return "BMI:\t\t" + str(bmi) + "\n"
def prepare_kcal_text(kcal):
    return str(kcal) + " kcal            "

def rotatePoint(centerPoint,point,angle,output):
	"""Rotates a point around another centerPoint. Angle is in degrees.
	Rotation is counter-clockwise"""
	angle = 360 - angle 
	""" Rotation is now clockwise """
	angle = radians(angle)
	temp_point = point[0]-centerPoint[0] , point[1]-centerPoint[1]
	# 300/(260-20)=1.25
	temp_point = ( temp_point[0]*cos(angle)-(temp_point[1]*sin(angle)) , ((temp_point[0]*sin(angle))+temp_point[1]*cos(angle))*1.25)
	temp_point = temp_point[0]+centerPoint[0] , temp_point[1]+centerPoint[1]
	rotatedPoint= str(temp_point[0]) + " " + str(temp_point[1])
	if output=='dialPath':
		return rotatedPoint
	elif output=='x':
		return str(temp_point[0])
	elif output=='y':
		return str(temp_point[1])


def gaugeDiv(baseLabels, meterLabels, colors, value, suffix):
	meterValues = []
	meterValues.append(0)
	meterSum = 0
	# Calculate steps. Then first value is the sum of all the others.
	for i in range(1, len(baseLabels)-1):
		meterValues.append(float(baseLabels[i+1]) - float(baseLabels[i]))
		meterSum += meterValues[i]

	meterValues[0] = meterSum

	# Dial path. Apply angle from full left position.
	rangeValue = float(meterValues[0])
	minValue=float(baseLabels[1])
	chartCenter=0.5
	dialTip=chartCenter-0.12
	dialAngle=(value-minValue)*180/rangeValue
	dialPath = 'M ' + rotatePoint((chartCenter,0.5),(chartCenter,0.485),dialAngle, 'dialPath') + ' L ' + rotatePoint((chartCenter,0.5),(dialTip,0.5),dialAngle, 'dialPath') + ' L ' + rotatePoint((chartCenter,0.5),(chartCenter,0.515),dialAngle, 'dialPath') + ' Z'
	infoText=(str(value) + str(suffix))

	# Gauge
	meterChart = go.Pie(
		values=meterValues, labels=meterLabels,
		marker=dict(colors=colors, 
			line=dict(width=0) # Switch line width to 0 in production
			),
		name="Gauge", hole=.3, direction="clockwise", rotation=90,
		showlegend=False, textinfo="label", textposition="inside", hoverinfo="none",
		sort=False
			)

	# Layout
	layout = go.Layout(
		xaxis=dict(showticklabels=False, autotick=False, showgrid=False, zeroline=False,),
		yaxis=dict(showticklabels=False, autotick=False, showgrid=False, zeroline=False,),
		shapes=[dict(
				type='path', path=dialPath, fillcolor='rgba(44, 160, 101, 1)',
				line=dict(width=0.5), xref='paper', yref='paper'),
		],
		annotations=[
			dict(xref='paper', yref='paper', x=(chartCenter-0.015), y=0.2, text=infoText, font=dict(size='20', color='#ffffff'), showarrow=False),
		],
		height=260, width=300, margin=dict(l=0, r=0, t=20, b=0, autoexpand=False), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
			)

	# Write static values as annotations
	for value in baseLabels:
		if value is not '-':
			annotationDict=dict(
					xref='paper', yref='paper', xanchor='center', yanchor='middle', 
						x=rotatePoint((chartCenter,0.5),((chartCenter-0.45),0.5), ((float(value)-minValue)*180/rangeValue), 'x'), 
						y=rotatePoint((chartCenter,0.5),((chartCenter-0.45),0.5), ((float(value)-minValue)*180/rangeValue), 'y'),
						font=dict(size='12', color='#ffffff'), showarrow=False, text=value, 
				)

			layout['annotations'].append(annotationDict)

	# Build HTML div
	div = plotly.plot(dict(data=[meterChart], layout=layout), include_plotlyjs=False, show_link=False, output_type='div')

	return div

def barDiv(slope, value, suffix, bar_suffix, bar_format, color, layoutRange):
	infoText=(str(value) + str(suffix))
	tendancy = (slope*timedelta(days=7).total_seconds()) # ToDO: round instead

	if tendancy > 0:
		tendancyText="+"
		tendancyOrigin=0.825
	else:
		tendancyText=""
		tendancyOrigin=0.675

	
	tendancyText+=str(bar_format % tendancy)+' '+bar_suffix
	tendancyPosition=tendancyOrigin+((1.2*tendancy)/layoutRange[1]/4)

	# Bar
	barChart = go.Bar(
		x=['tendancy',], y=[float(tendancy),],
		name="Bar", showlegend=False, hoverinfo="none",	marker=dict(color=color),	
			)

	# Layout
	layout = go.Layout(
		xaxis=dict(showticklabels=False, autotick=False, showgrid=False, zeroline=True, fixedrange=True, domain=[0, 1], ),
		yaxis=dict(showticklabels=False, autotick=False, showgrid=False, zeroline=False, fixedrange=True, domain=[0.5, 1], range=layoutRange, ),
		annotations=[ 
			dict(xref='paper', yref='paper', x=0.5, y=0, text=infoText, font=dict(size='20', color='#ffffff'), xanchor='center', yanchor='middle', showarrow=False),
			dict(xref='paper', yref='paper', x=0.5, y=tendancyPosition, text=tendancyText, font=dict(size='14', color='#ffffff'), xanchor='center', yanchor='middle', showarrow=False),
		],
		height=260, width=120, margin=dict(l=0, r=0, t=40, b=40, autoexpand=False), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)"
			)

	# Build HTML div
	div = plotly.plot(dict(data=[barChart], layout=layout), include_plotlyjs=False, show_link=False, output_type='div')

	return div

#-----------------------------------------------------------------------------------------
# Get arguments
parser = argparse.ArgumentParser(description='Plot body data from smart scale.')
parser.add_argument('-p','--person', help='Person ID',required=True)
parser.add_argument('-w','--window',help='Time window in days.', required=True)
args = parser.parse_args()

# Parameters
personID = int(args.person)
timeWindow = int(args.window)
dirname = os.path.dirname(__file__)
csvFile = '../BS440csv/' + str(personID) + '.csv'
csvPath = os.path.join(dirname, csvFile)

# BS440webapp config
config = SafeConfigParser()
config.read('BS440webapp.ini')
personsection = 'Person' + str(personID)

# Set up Logging
numeric_level = getattr(logging,
                        config.get('Program', 'loglevel').upper(),
                        None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % loglevel)
logging.basicConfig(level=numeric_level,
                    format='%(asctime)s %(levelname)-8s %(funcName)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='BS440plot.log',
                    filemode='a')
log = logging.getLogger(__name__)

# Grab person details
if config.has_section(personsection):
	person = config.get(personsection, 'username')
	gender = config.get(personsection, 'gender')
	goal = config.get(personsection, 'goal')
else:
	log.error('Unable to plot: No details found in ini file for person %d. Exiting.' % personID)
	sys.exit(127)

#-----------------------------------------------------------------------------------------
# Import data from csv
df = pd.read_csv(csvPath, header=None, names=['timestamp','weight','fat','muscle','bone','water','kcal','bmi'])

# Retrieve most recent timestamp
last_timestamp=df['timestamp'].iat[-1]

# Calcultate the timestamp equal to the last timestamp minus the given time window
min_timestamp = (datetime.fromtimestamp(int(last_timestamp)) - timedelta(days=timeWindow)).strftime('%s')

# Tail the data frame
df = df[(df.timestamp > int(min_timestamp))]

# Retrieve oldest timestamp
first_timestamp = df.loc[df.index[0], 'timestamp']

# Create datetime from timestamp
df['datetime'] = df['timestamp'].apply(convert_to_datetime)

# Retrieve most recent values
last_weight=df['weight'].iat[-1]
last_fat=df['fat'].iat[-1]
last_muscle=df['muscle'].iat[-1]
last_bone=df['bone'].iat[-1]
last_water=df['water'].iat[-1]
last_kcal=df['kcal'].iat[-1]
last_bmi=df['bmi'].iat[-1]
last_datetime=df['datetime'].iat[-1]

# Prepare text from weight and suffix kg
df['weightText'] = df['weight'].apply(prepare_weight_text)

# Prepare hover data
df['fatText'] = df['fat'].apply(prepare_fat_text)
df['muscleText'] = df['muscle'].apply(prepare_muscle_text)
df['boneText'] = df['bone'].apply(prepare_bone_text)
df['waterText'] = df['water'].apply(prepare_water_text)
df['kcalText'] = df['kcal'].apply(prepare_kcal_text)
df['bmiText'] = df['bmi'].apply(prepare_bmi_text)
df['dataText'] = df['fatText'] + df['muscleText'] + df['waterText'] + df['boneText'] + df['bmiText'] + df['kcalText']

#-----------------------------------------------------------------------------------------
# Configure main plot
#-----------------------------------------------------------------------------------------

# Weight tendancy
weightSlope, weightIntercept, weight_r_value, weight_p_value, weight_std_err = stats.linregress(df['timestamp'],df['weight'])
weightTendancyLine = weightSlope*df['timestamp']+weightIntercept

if (float(goal) > last_weight) and (weightSlope > 0):
	weightBarColor=['rgb(51,255,102)',]
elif (float(goal) < last_weight) and (weightSlope < 0):
	weightBarColor=['rgb(51,255,102)',]
else:
	weightBarColor=['rgb(255,102,0)',]


weightDiv = barDiv(weightSlope*1000, last_weight, 'kg<br>Weight', '<br>g/week', '%.0f', weightBarColor, [-2000,2000])

tendancyTrace = go.Scatter(
	x=df['timestamp'], y=weightTendancyLine, # Data
	mode='lines', name='Tendancy', hoverinfo='none', visible=False # Additional options
                   )

# Traces
weightTrace = go.Scatter(
	x=df['timestamp'], y=df['weight'], # Data
	mode='markers+lines+text', text=df['weightText'], textposition='top center', textfont=dict(size='16', color='#1f77b4'), name='weight',
	line=dict(shape='spline', smoothing='0.5'), hoverinfo='none', # Additional options
                   )
dataTrace = go.Scatter(
	x=df['timestamp'], y=df['weight'], # Data
	mode='markers', name='', text=df['dataText'], hoverinfo='text', # Additional options
                   )
goalTrace = go.Scatter(
	x=[first_timestamp, last_timestamp], y=[goal, goal], # Data
	mode='lines', name='goal', line=dict(shape='spline', smoothing='0.5'), hoverinfo='none', # Additional options
                   )

traceData=[weightTrace, dataTrace, goalTrace, tendancyTrace]

# If tick labels (date and time on x axis) are too long, increase bottom margin and height to give room
layoutBottomRoom=0
layoutHeight=450+layoutBottomRoom
layoutBottomMargin=80+layoutBottomRoom

weightLayout = go.Layout(
	title = person + ' Body Weight (kg)', titlefont=dict(size='20', color='#ffffff'),
	showlegend=False, height=layoutHeight, margin=dict(l=40, r=40, t=60, b=layoutBottomMargin),
	xaxis=dict(showticklabels=True, tickvals=df['timestamp'], ticktext=df['datetime'], tickfont=dict(size='14', color='#ffffff'), ),
	yaxis=dict(mirror='ticks', tickfont=dict(size='14', color='#ffffff')), paper_bgcolor="rgba(0,0,0,0)"
              )

weightFig = dict(data=traceData, layout=weightLayout)

# Plot weight trace 
plotDiv = plotly.plot(weightFig, include_plotlyjs=False, show_link=False, output_type='div')

#-----------------------------------------------------------------------------------------
# Configure gauges
#-----------------------------------------------------------------------------------------

# BMI gauge
bmiDiv = gaugeDiv(["-", "14", "18.5", "25", "30", "40"], 
	[" ", "Underweight", "Normal", "Overweight", "Obese"], 
	['rgba(0,0,0,0)','rgb(204,204,204)','rgb(51,255,102)','rgb(255,255,51)','rgb(255,102,0)'], 
	last_bmi, '<br>BMI')

# Fat gauge
if gender == 'male':
	fatBaseLabels = ["-", "2", "6", "13", "17", "22", "30", "40"]	

elif gender == 'female':
	fatBaseLabels = ["-", "10", "14", "21", "25", "31", "40", "50"]

fatDiv = gaugeDiv(fatBaseLabels, 
	[" ", "Essential fat", "Athlete", "Fitness", "Average", "Overweight", "Obese"], 
	['rgba(0,0,0,0)','rgb(204,204,204)','rgb(102,255,153)','rgb(51,255,102)','rgb(255,255,51)','rgb(255,153,51)','rgb(255,102,0)'], 
	last_fat, '%<br>Fat')

# Water gauge
if gender == 'male':
	if last_fat >= 4 and last_fat < 15:
		waterBaseLabels = ["-", "30", "63", "70", "80"]
	if last_fat >= 15 and last_fat < 22:
		waterBaseLabels = ["-", "30", "57", "63", "80"]
	if last_fat >= 22 and last_fat < 25:
		waterBaseLabels = ["-", "30", "55", "57", "80"]
	if last_fat >= 25:
		waterBaseLabels = ["-", "30", "37", "55", "80"]

elif gender == 'female':
	if last_fat >= 4 and last_fat < 21:
		waterBaseLabels = ["-", "30", "58", "70", "80"]
	if last_fat >= 21 and last_fat < 30:
		waterBaseLabels = ["-", "30", "52", "58", "80"]
	if last_fat >= 30 and last_fat < 33:
		waterBaseLabels = ["-", "30", "49", "52", "80"]
	if last_fat >= 33:
		waterBaseLabels = ["-", "30", "37", "49", "80"]

waterDiv = gaugeDiv(waterBaseLabels, 
	[" ", "Low", "Optimal", "High"], 
	['rgba(0,0,0,0)','rgb(255,255,51)','rgb(51,255,102)','rgb(255,255,51)'], 
	last_water, '%<br>Water')

# Fat tendancy
fatSlope, fatIntercept, fat_r_value, fat_value, fat_std_err = stats.linregress(df['timestamp'],df['fat'])
fatTendancyLine = fatSlope*df['timestamp']+fatIntercept

if fatSlope < 0:
	fatBarColor=['rgb(51,255,102)',]
else:
	fatBarColor=['rgb(255,102,0)',]

fatBarDiv = barDiv(fatSlope, last_fat, '%<br>Fat', '<br>%/week', '%.2f', fatBarColor, [-0.6,0.6])

# Muscle tendancy
muscleSlope, muscleIntercept, muscle_r_value, muscle_value, muscle_std_err = stats.linregress(df['timestamp'],df['muscle'])
muscleTendancyLine = muscleSlope*df['timestamp']+muscleIntercept

if muscleSlope > 0:
	muscleBarColor=['rgb(51,255,102)',]
else:
	muscleBarColor=['rgb(255,102,0)',]

muscleDiv = barDiv(muscleSlope, last_muscle, '%<br>Muscle', '<br>%/week', '%.2f', muscleBarColor, [-0.6,0.6])

# kCal tendancy
kcalSlope, kcalIntercept, kcal_r_value, kcal_value, kcal_std_err = stats.linregress(df['timestamp'],df['kcal'])
kcalTendancyLine = kcalSlope*df['timestamp']+kcalIntercept

kcalDiv = barDiv(kcalSlope, last_kcal, 'kcal<br>Needs', '<br>kcal/week', '%.0f', weightBarColor, [-100,100])

# Bone tendancy
boneSlope, boneIntercept, bone_r_value, bone_value, bone_std_err = stats.linregress(df['timestamp'],df['bone'])
boneTendancyLine = boneSlope*df['timestamp']+boneIntercept

if boneSlope > 0:
	boneBarColor=['rgb(51,255,102)',]
else:
	boneBarColor=['rgb(255,102,0)',]

boneDiv = barDiv(boneSlope*1000, last_bone, 'kg<br>Bone', '<br>g/week', '%.0f', boneBarColor, [-100,100])

#-----------------------------------------------------------------------------------------
# Build HTML
#-----------------------------------------------------------------------------------------

# Prepare HTML
plotlyHTML = """
	<div id="trace">
	"""
plotlyHTML += plotDiv
plotlyHTML += """
	</div><br/>"""
plotlyHTML += """
	<div id="gaugesandbars">
		<div id="gauges">
			<div class="gauge">
			"""
plotlyHTML += bmiDiv + """
			</div>"""
plotlyHTML += """
			<div class="gauge">
			"""
plotlyHTML += fatDiv + """
			</div>"""
plotlyHTML += """
			<div class="gauge">
			"""
plotlyHTML += waterDiv + """
			</div>"""
plotlyHTML += """
		</div>
		<div id="bars">
			<div class="bar">
			"""
plotlyHTML += weightDiv + """
			</div>"""
plotlyHTML += """
			<div class="bar">
			"""
plotlyHTML += fatBarDiv + """
			</div>"""
plotlyHTML += """
			<div class="bar">
			"""
plotlyHTML += muscleDiv + """
			</div>"""
plotlyHTML += """
			<div class="bar">
			"""
plotlyHTML += kcalDiv + """
			</div>"""
plotlyHTML += """
			<div class="bar">
		"""
plotlyHTML += boneDiv + """
			</div>
		</div>
	</div>"""

# Generate template to be used by Flask
fileName= './templates/plot-' + str(personID) + '-' + str(timeWindow) + '.html'

try:
	f = open(fileName,'w')
	f.write(plotlyHTML)
	f.close()
	log.info('Plot file %s generated successfully for user %s.' % (fileName, person) )

except:
	log.error('Failed to generate plot file %s for user %s.' % (fileName, person) )
	sys.exit(126)

