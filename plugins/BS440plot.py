import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly
from plotly import tools
import argparse
from datetime import datetime, timedelta
import webbrowser
__author__ = 'DjZU'


# Get arguments
parser = argparse.ArgumentParser(description='Plot body data from smart scale.')
parser.add_argument('-p','--person', help='Person',required=True)
parser.add_argument('-w','--window',help='Time window in days.', required=True)
args = parser.parse_args()
 
# Parameters
person = args.person
csvFile = person.lower() + '.csv'
fileName= person.lower() + '-plot.html'
timeWindow = int(args.window)

# Import data from csv
df = pd.read_csv(csvFile, header=None, names=['timestamp','weight','fat','muscle','bone','water','kcal','bmi'])

# Process data from csv
def convert_to_datetime(timestamp):
    return datetime.fromtimestamp(int(timestamp)).strftime('%A, %b %-d %Y %-H:%M')

df['datetime'] = df['timestamp'].apply(convert_to_datetime)

# Calcultate the timestamp equal to the last timestamp minus the given time window
first_timestamp = (datetime.fromtimestamp(int(df['timestamp'].iat[-1])) - timedelta(days=timeWindow)).strftime('%s')
#print first_timestamp

df = df[(df.timestamp > int(first_timestamp))]

# Retrieve most recent values
last_datetime=df['datetime'].iat[-1]
last_weight=df['weight'].iat[-1]
last_fat=df['fat'].iat[-1]
last_muscle=df['muscle'].iat[-1]
last_bone=df['bone'].iat[-1]
last_water=df['water'].iat[-1]
last_kcal=df['kcal'].iat[-1]
last_bmi=df['bmi'].iat[-1]

# Configure traces
trace1 = go.Scatter(
                    x=df['timestamp'], y=df['weight'], # Data
                    text=df['datetime'], mode='markers+lines', name='weight', line=dict(shape='spline', smoothing='0.5') # Additional options
                   )
trace2 = go.Scatter(x=df['timestamp'], y=df['fat'], text=df['datetime'], mode='markers+lines', name='fat', line=dict(shape='spline', smoothing='0.5') )
trace3 = go.Scatter(x=df['timestamp'], y=df['muscle'], text=df['datetime'], mode='markers+lines', name='muscle', line=dict(shape='spline', smoothing='0.5') )
trace4 = go.Scatter(x=df['timestamp'], y=df['bone'], text=df['datetime'], mode='markers+lines', name='bone', line=dict(shape='spline', smoothing='0.5') )
trace5 = go.Scatter(x=df['timestamp'], y=df['water'], text=df['datetime'], mode='markers+lines', name='water', line=dict(shape='spline', smoothing='0.5') )
trace6 = go.Scatter(x=df['timestamp'], y=df['kcal'], text=df['datetime'], mode='markers+lines', name='kcal', line=dict(shape='spline', smoothing='0.5') )
trace7 = go.Scatter(x=df['timestamp'], y=df['bmi'], text=df['datetime'], mode='markers+lines', name='bmi', line=dict(shape='spline', smoothing='0.5') )

# Configure subplots
fig = tools.make_subplots(rows=7, cols=1, subplot_titles=('Weight', 'Fat %', 'Muscle %', 'Water %', 'kCal needs', 'BMI', 'Bone mass'), vertical_spacing='0.02')
fig.append_trace(trace1, 1, 1)
fig.append_trace(trace2, 2, 1)
fig.append_trace(trace3, 3, 1)
fig.append_trace(trace5, 4, 1)
fig.append_trace(trace6, 5, 1)
fig.append_trace(trace7, 6, 1)
fig.append_trace(trace4, 7, 1)

fig['layout'].update(height=3000, title=person+' body data', showlegend=False)
fig['layout']['xaxis'].update(showticklabels=False)
fig['layout']['xaxis2'].update(showticklabels=False)
fig['layout']['xaxis3'].update(showticklabels=False)
fig['layout']['xaxis4'].update(showticklabels=False)
fig['layout']['xaxis5'].update(showticklabels=False)
fig['layout']['xaxis6'].update(showticklabels=False)
fig['layout']['xaxis7'].update(showticklabels=False)

# Plot data 
plot_div = plotly.offline.plot(fig, output_type='div')

# Build HTML
f = open(fileName,'w')

message = """<html>
<head>
	<title>""" + person + """ body data</title>
</head>
<body>
<p align="center" style="font-family:'Open Sans',verdana, arial, sans-serif; font-size:48px;">Last Measurements</p>
<p align="left" style="font-family:'Open Sans', verdana, arial, sans-serif; font-size:16px;">"""

message += "Date: " + str(last_datetime) + "<br/>"
message += "Weight: " + str(last_weight) + "<br/>"
message += "Fat %: " + str(last_fat) + "<br/>"
message += "Muscle %: " + str(last_muscle) + "<br/>"
message += "Water %: " + str(last_water) + "<br/>"
message += "kCal needs: " + str(last_kcal) + "<br/>"
message += "BMI: " + str(last_bmi) + "<br/>"
message += "Bone mass: " + str(last_bone) + "<br/></p><p>"

message += plot_div + """
</p></body>
</html>"""

f.write(message)
f.close()

webbrowser.open_new_tab(fileName)
