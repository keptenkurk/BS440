'''
BS440domoticz.py
Update weight value to Domoticz home automation system
'''
import urllib2
import base64
import logging


def UpdateDomoticz(config, weightdata):
    log = logging.getLogger(__name__)
    domoticzurl = config.get('Domoticz', 'domoticz_url')
    domoticzuser = config.get('Domoticz', 'domoticz_user')
    domoticzpwd = config.get('Domoticz', 'domoticz_pwd')
    personsection = 'Person' + str(weightdata[0]['person'])
    if config.has_section(personsection):
        domoticzidx = config.get(personsection, 'domoticz_idx')
        scaleuser = config.get(personsection, 'username')
    else:
        log.error('Unable to update Domoticz: No details found in ini file '
                  'for person %d' % (weightdata[0]['person']))
        return
    try:
        log.info('Updating Domoticz for user %s at index %s with weight %s' % (
                  scaleuser, domoticzidx, weightdata[0]['weight']))
        url = 'http://%s/json.htm?type=command&param=udevice&hid=2&' \
              'did=%s&dunit=4&dtype=93&dsubtype=1&nvalue=0&svalue=%s' % (
               domoticzurl, domoticzidx, weightdata[0]['weight'])
        log.debug('calling url: %s' % (url))
        req = urllib2.Request(url)
        base64string = base64.encodestring('%s:%s' % (
                       domoticzuser, domoticzpwd)).replace('\n', '')
        req.add_header('Authorization', 'Basic %s' % base64string)
        resp = urllib2.urlopen(req)
        log.info('Domoticz succesfully updated')
    except:
        log.error('Unable to update Domoticz: Error sending data.')
