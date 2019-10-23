#-----------------------------------------------------------------------------------------
# BS440 plugin Google fit  BS440google.py
# About:
# This plugin updates a Google fit account with scale data
#
# Any personalization or parameters can be found in BS440google.ini
# Note: The plugin is now an object of class Plugin which affects the way of how
# to declare functions and the way to use them. See BS440mail.py as example
#
#
#
#------------------------------------------------------------------------------------------
from ConfigParser import SafeConfigParser
import logging
import os
import httplib2
import sys
import time
import yaml
import argparse
import datetime
import dateutil.tz
import dateutil.parser
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2Credentials
from googleapiclient.errors import HttpError


class Plugin:

    def __init__(self):
        # put any commands here you would like to be run to initialize your plugin
        return
        

    def nano(self, val):
        """Converts a number to nano (str)."""
        return '%d' % (val * 1e9)


    def GetGoogleClient(self, filename):
        global log
        log.info("Creating Google client")
        log.info("Reading auth file %s", filename)
        credentials = Storage(filename).get()
        http = credentials.authorize(httplib2.Http())
        client = build('fitness', 'v1', http=http)
        log.info("Google client created")
        return client


    def CreateDataSource(self, newDataType):
        """
        Return a specific DataSource based on a generic skeleton.
        Needs a dict.
        """
        return dict(
            type='raw',
            application=dict(name='BS440'),
            dataType=newDataType,
            device=dict(
                type='scale',
                manufacturer='unknown',
                model='unknown',
                uid='10000001',
                version='1',
                )
            )


    def CheckDataSource(self, googleClient, dataSourceId, dataSource):
        """Ensure datasource exists for the device or create if not"""
        try:
            googleClient.users().dataSources().get(
                userId='me',
                dataSourceId=dataSourceId).execute()
        except HttpError, error:
            if 'DataSourceId not found' not in str(error):
                raise error
                googleClient.users().dataSources().create(
                    userId='me', body=dataSource).execute()


    def AddGoogle(self, googleClient, value, typeofdata, googleauthfile):
        global log
        minLogNs = self.nano(time.time())
        maxLogNs = self.nano(time.time())
        datasetId = '%s-%s' % (minLogNs, maxLogNs)
        log.info('Created a new dataset: %s' % (datasetId))

        dataType = dict(
            name=typeofdata['dataName'],
            field=[dict(format=typeofdata['fieldFormat'],
                        name=typeofdata['fieldName'])])
        dataSource = self.CreateDataSource(dataType)
        dataSourceId = self.GetDataSourceId(googleClient,
                                       self.CreateDataSource(dataType),
                                       googleauthfile)

        # if data source does not exiest, create it
        self.CheckDataSource(googleClient, dataSourceId, dataSource)
        log.info('Data Source ID: %s' % (dataSourceId))

        googleClient.users().dataSources().datasets().patch(
            userId='me',
            dataSourceId=dataSourceId,
            datasetId=datasetId,
            body=dict(
                dataSourceId=dataSourceId,
                maxEndTimeNs=maxLogNs,
                minStartTimeNs=minLogNs,
                point=[dict(
                    dataTypeName=typeofdata['dataName'],
                    endTimeNanos=maxLogNs,
                    startTimeNanos=minLogNs,
                    value=[dict(fpVal=value)],), ],
                        )
                    ).execute()


    def GetDataSourceId(self, googleClient, dataSource, googleauthfile):
        projectNumber = Storage(googleauthfile).get().client_id.split('-')[0]
        return ':'.join((
            dataSource['type'],
            dataSource['dataType']['name'],
            projectNumber,
            dataSource['device']['manufacturer'],
            dataSource['device']['model'],
            dataSource['device']['uid']))

        
    def execute(self, globalconfig, persondata, weightdata, bodydata):
        global log
        # --- part of plugin skeleton
        # your plugin receives the config details from BS440.ini as well as
        # all the data received frm the scale
        log = logging.getLogger(__name__)
        log.info('Starting plugin: ' + __name__)
        #read ini file from same location as plugin resides, named [pluginname].ini
        configfile = os.path.dirname(os.path.realpath(__file__)) + '/' + __name__ + '.ini'
        pluginconfig = SafeConfigParser()
        pluginconfig.read(configfile)
        log.info('ini read from: ' + configfile)

        # Thats it! From here do your thing with the data.
        # Be sure to catch and log errors if you're doing risky stuff  
        POUNDS_PER_KILOGRAM = 2.20462
        TIME_FORMAT = "%a, %d %b %Y %H:%M:%S"
        WEIGHTD = {'dataName': 'com.google.weight',
           'fieldFormat': 'floatPoint', 'fieldName': 'weight'}
        FATD = {'dataName': 'com.google.body.fat.percentage',
        'fieldFormat': 'floatPoint', 'fieldName': 'percentage'}        
        personsection = 'Person' + str(weightdata[0]['person'])
        scaleuser = pluginconfig.get(personsection, 'username')
        googleauthfile = pluginconfig.get(personsection, 'googleauthfile')
        log.info('Updating Google Fit for user %s with weight %s and google authfile: %s' %
                 (scaleuser, weightdata[0]['weight'], googleauthfile))
        try:
            self.googleClient = self.GetGoogleClient(googleauthfile)
            self.AddGoogle(self.googleClient, weightdata[0]['weight'], WEIGHTD, googleauthfile)
            self.AddGoogle(self.googleClient, bodydata[0]['fat'], FATD, googleauthfile)
        except:
            log.error('Unable to update Google Fit: Error sending data.')

        # finally end this plugin execution with
        log.info('Finished plugin: ' + __name__)