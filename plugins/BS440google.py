'''
Google allows us to update the weight on Fit.
Create an oauthfile before using this feature (auth_google.py)
'''


import httplib2
import sys
import time
import yaml
import argparse
import logging
import datetime
import dateutil.tz
import dateutil.parser
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2Credentials
from googleapiclient.errors import HttpError


POUNDS_PER_KILOGRAM = 2.20462
TIME_FORMAT = "%a, %d %b %Y %H:%M:%S"
WEIGHTD = {'dataName': 'com.google.weight',
           'fieldFormat': 'floatPoint', 'fieldName': 'weight'}
FATD = {'dataName': 'com.google.body.fat.percentage',
        'fieldFormat': 'floatPoint', 'fieldName': 'percentage'}


def nano(val):
    """Converts a number to nano (str)."""
    return '%d' % (val * 1e9)


def GetGoogleClient(filename):
    log.info("Creating Google client")
    log.info("Reading auth file %s", filename)
    credentials = Storage(filename).get()
    http = credentials.authorize(httplib2.Http())
    client = build('fitness', 'v1', http=http)
    log.info("Google client created")
    return client


def CreateDataSource(newDataType):
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


def CheckDataSource(googleClient, dataSourceId, dataSource):
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


def AddGoogle(googleClient, value, typeofdata, googleauthfile):
    minLogNs = nano(time.time())
    maxLogNs = nano(time.time())
    datasetId = '%s-%s' % (minLogNs, maxLogNs)
    log.info('Created a new dataset: %s' % (datasetId))

    dataType = dict(
        name=typeofdata['dataName'],
        field=[dict(format=typeofdata['fieldFormat'],
                    name=typeofdata['fieldName'])])
    dataSource = CreateDataSource(dataType)
    dataSourceId = GetDataSourceId(googleClient,
                                   CreateDataSource(dataType),
                                   googleauthfile)

    # if data source does not exiest, create it
    CheckDataSource(googleClient, dataSourceId, dataSource)
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


def GetDataSourceId(googleClient, dataSource, googleauthfile):
    projectNumber = Storage(googleauthfile).get().client_id.split('-')[0]
    return ':'.join((
        dataSource['type'],
        dataSource['dataType']['name'],
        projectNumber,
        dataSource['device']['manufacturer'],
        dataSource['device']['model'],
        dataSource['device']['uid']))


def UpdateGoogle(config, persondata, weightdata, bodydata):
    personsection = 'Person' + str(weightdata[0]['person'])
    scaleuser = config.get(personsection, 'username')
    googleauthfile = config.get(personsection, 'googleauthfile')
    log.info('Updating Google Fit for user %s with weight %s and google authfile: %s' %
             (scaleuser, weightdata[0]['weight'], googleauthfile))
    try:
        googleClient = GetGoogleClient(googleauthfile)
        AddGoogle(googleClient, weightdata[0]['weight'], WEIGHTD, googleauthfile)
        AddGoogle(googleClient, bodydata[0]['fat'], FATD, googleauthfile)
    except:
        log.error('Unable to update Google Fit: Error sending data.')
