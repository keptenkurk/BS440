# coding: utf-8
# -----------------------------------------------------------------------------------------
# BS440 plugin BS440influxdb.py
# About:
# Store collected data in InlfuxDB (e.g. for Grafana)
#
import logging
import os
import json
import ssl
import datetime as dt
from influxdb import InfluxDBClient

from configparser import ConfigParser

__author__ = 'Chris van Marle'
__email__ = "qistoph@@gmail.com"
__license__ = "EUPL-1.1"
__version__ = "0.0.1"
__status__ = "Development"
# ------------------------------------------------------------------------------------------

logger = logging.getLogger(__name__)

class Plugin:
    def __init__(self):
        """ Reads config file """
        logger.info('Initialising plugin: ' + __name__)

        # read ini file from same location as plugin resides, named [pluginname].ini
        configfile = os.path.dirname(os.path.realpath(__file__)) + '/' + __name__ + '.ini'
        plugin_config = ConfigParser()
        plugin_config.read(configfile)
        logger.info('Read config from: ' + configfile)

        # create configuration arguments for influxdb client
        influx_config = dict(plugin_config.items('InfluxDB'))
        self.measurement_name = influx_config['measurement']
        self.influx_client = InfluxDBClient(
                host=influx_config['hostname'], port=int(influx_config['port']), database=influx_config['database'])

        if 'tags' in influx_config:
                self.tags = [t.strip() for t in influx_config.split(',')]
        else:
                self.tags = ['person']

        logger.debug('tags: ' + ','.join(self.tags))

    def timestamp_from_resultset(self, point):
        d = dt.datetime.strptime(point['time'], '%Y-%m-%dT%H:%M:%SZ')
        d = d.replace(tzinfo=dt.timezone.utc)
        ts = dt.datetime.timestamp(d)
        return ts

    def execute(self, globalconfig, persondata, weightdata, bodydata):
        """ Publishes weight and body data """

        if not persondata or not weightdata or not bodydata:
            logger.error('Invalid data...')
            return

        if len(weightdata) != len(bodydata):
            logger.error("Lengths of weightdata and bodydata don't match")
            return

        person_id = str(persondata[0]['person'])

        rs = self.influx_client.query("SELECT LAST(weight) FROM "+self.measurement_name+" WHERE person = $person", bind_params={'person':person_id})
        points = list(rs.get_points())
        if len(points) > 0:
            last_time = self.timestamp_from_resultset(next(rs.get_points()))
        else:
            last_time = 0
        logger.debug('Getting results after {}'.format(last_time))

        for n in range(len(weightdata), 0, -1):
            idx = n - 1
            if weightdata[idx]['timestamp'] <= last_time:
                continue

            logger.debug("Updating data from {}".format(weightdata[idx]['timestamp']))

            # construct payload
            model = globalconfig.get('Scale', 'device_model')
            payload = dict(weightdata[idx])
            payload.update(bodydata[idx])
            payload.update(persondata[0])
            payload['model'] = model

            tags = {k: v for k, v in payload.items() if k in self.tags}
            for k in tags.keys():
                    del payload[k]

            ts = payload['timestamp']
            del payload['timestamp']

            influx_msg = {
                    'measurement': self.measurement_name,
                    'fields': payload,
                    'time': ts
            }

            logger.info('Publishing data of person {}'.format(person_id))
            logger.debug('Influx msg: {}'.format(json.dumps(influx_msg)))

            self.influx_client.write_points(
                    points = [influx_msg],
                    time_precision = 's',
                    tags = tags
            )
