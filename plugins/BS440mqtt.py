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

from configparser import SafeConfigParser
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
                          'port': int(mqtt_config['port']),
                          'retain': True}
        self.ad_config = dict(plugin_config.items('AUTO_DISCOVERY'))

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
                          
        if 'ha_auto_discovery' in self.ad_config:
            self.ad_config["ha_auto_discovery"] = self.ad_config['ha_auto_discovery'].lower() == "true"

        logger.info('Publishing init topic')
        publish.single(topic='bs440/init/', payload='BS440 initialised', **self.mqtt_args)

    def broadcast_auto_discovery(self, model, person):
        model_lower = model.lower()
        measurements = [
            {"ha_value": "weight", "scale_value": "weight", "name": "Weight", "icon": "scale-bathroom", "unit": "kg"},
            {"ha_value": "calories", "scale_value": "kcal", "name": "Calories", "icon": "fire", "unit": "kcal"},
            {"ha_value": "fat", "scale_value": "fat", "name": "Fat", "icon": "account-group", "unit": "%"},
            {"ha_value": "water", "scale_value": "tbw", "name": "Water Ratio", "icon": "water-opacity", "unit": "%"},
            {"ha_value": "muscle", "scale_value": "muscle", "name": "Muscle Ratio", "icon": "weight-lifter", "unit": "%"},
            {"ha_value": "bone", "scale_value": "bone", "name": "Bone Mass", "icon": "bone", "unit": "kg"},
            {"ha_value": "bmi", "scale_value": "bmi", "name": "BMI", "icon": "calculator-variant-outline", "unit": ""}
        ]
        for measurement in measurements:
            identifier = model_lower + "_" + person.lower()
            measurement_identifier = identifier + "_" + measurement["ha_value"]
            device = {"mdl": model, "name": model + " " + person, "mf": "Medisana", "identifiers": [identifier]}
            ad_topic = 'homeassistant/sensor/{}/{}/config'.format(identifier, measurement["ha_value"])
            ad_payload = {"name": measurement["name"], "value_template": "{{{{ value_json.{} }}}}".format(measurement["scale_value"]), "unit_of_measurement": measurement["unit"], "icon":"mdi:" + measurement["icon"], "state_topic": "homeassistant/sensor/{}/state".format(identifier), "object_id": measurement_identifier, "unique_id": measurement_identifier, "device": device }
            logger.info('Publishing Auto Discovery for {}'.format(measurement["scale_value"]))
            logger.debug(ad_topic)
            logger.debug(str(ad_payload))
            publish.single(topic=ad_topic,
                        payload=json.dumps(ad_payload),
                        **self.mqtt_args)

    def execute(self, globalconfig, persondata, weightdata, bodydata):
        """ Publishes weight and body data """

        if not persondata or not weightdata or not bodydata:
            logger.error('Invalid data...')
            return

        person_id = str(persondata[0]['person'])
        person_identifier = "person" + person_id
        if (person_identifier in self.ad_config):
            person_identifier = self.ad_config[person_identifier]

        # construct payload
        model = globalconfig.get('Scale', 'device_model')
        payload = dict(weightdata[0])
        payload.update(bodydata[0])
        payload.update(persondata[0])
        payload['model'] = model
        payload['name'] = person_identifier

        if  self.ad_config["ha_auto_discovery"]:
            self.broadcast_auto_discovery(model, person_identifier)

            logger.info('Publishing data of person {}'.format(person_id))
            publish.single(topic='homeassistant/sensor/{}_{}/state'.format(model.lower(), person_identifier.lower()),
                       payload=json.dumps(payload),
                       **self.mqtt_args)
        else:
            publish.single(topic='{}/{}/'.format(model.lower(), person_identifier.lower()),
                       payload=json.dumps(payload),
                       **self.mqtt_args)
