# coding: utf-8
# -----------------------------------------------------------------------------------------
# BS440 plugin BS440mqtt.py
# About:
# Send collected data via MQTT (e.g. to Home Assistant)
#
# The corresponding configuration for Home Assistant looks like:

# sensor:
#     - platform: mqtt
#       state_topic: "bs440/person1/"
#       name: "Weight Person 1"
#       unit_of_measurement: "kg"
#       value_template: '{{ value_json.weight }}'
#     - platform: mqtt
#       state_topic: "bs440/person1/"
#       name: "Body Water Person 1"
#       unit_of_measurement: "%"
#       value_template: '{{ value_json.tbw }}'
#     - platform: mqtt
#       state_topic: "bs440/person1/"
#       name: "Body fat Person 1"
#       unit_of_measurement: "%"
#       value_template: '{{ value_json.fat }}'
#     - platform: mqtt
#       state_topic: "bs440/person1/"
#       name: "Muscle Mass Person 1"
#       unit_of_measurement: "%"
#       value_template: '{{ value_json.muscle }}'
#     - platform: mqtt
#       state_topic: "bs440/person1/"
#       name: "Bone Mass Person 1"
#       unit_of_measurement: "kg"
#       value_template: '{{ value_json.bone }}'

import logging
import os
import json
import ssl

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

        tls = {}
        if 'tls_cert' in mqtt_config:
            tls['ca_certs'] = mqtt_config['tls_cert']
        if 'tls_version' in mqtt_config:
            tls['tls_version'] = ssl.__getattribute__(mqtt_config['tls_version'])
        if len(tls) > 0:
            self.mqtt_args['tls'] = tls

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
