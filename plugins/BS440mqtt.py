# coding: utf-8
# -----------------------------------------------------------------------------------------
# BS440 plugin BS440mqtt.py
# About:
# Send collected data via MQTT (e.g. to Home Assistant)
#
import logging
import os
import json

from ConfigParser import SafeConfigParser
import paho.mqtt.publish as publish

__author__ = 'jinnerbichler'
__email__ = "j.innerbichler@gmail.com"
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
        plugin_config = SafeConfigParser()
        plugin_config.read(configfile)
        logger.info('Read config from: ' + configfile)

        # create configuration arguments for MQTT client
        mqtt_config = dict(plugin_config.items('MQTT'))
        self.mqtt_args = {'client_id': mqtt_config['client_id'],
                          'hostname': mqtt_config['hostname'],
                          'port': mqtt_config['port'],
                          'retain': True}
        if 'username' in mqtt_config:
            self.mqtt_args['auth'] = {'username': mqtt_config['username'],
                                      'password': mqtt_config['password']}

        publish.single(topic='bs440/init/', payload='BS440 initialised', **self.mqtt_args)

    def execute(self, globalconfig, persondata, weightdata, bodydata):
        """ Publishes weight and body data """

        if not persondata or not weightdata or not bodydata:
            logger.error('Invalid data...')
            return

        person_id = str(persondata[0]['person'])

        # construct payload
        model = globalconfig.get('Scale', 'device_model')
        payload = dict(weightdata[0])
        payload.update(bodydata[0])
        payload.update(persondata[0])
        payload['model'] = model

        logger.info('Publishing data of person {}'.format(person_id))

        publish.single(topic='bs440/person{}/'.format(person_id),
                       payload=json.dumps(payload),
                       **self.mqtt_args)
