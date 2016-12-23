'''
BS440domoticz.py
Update weight value to Domoticz home automation system
'''
#import urllib2
import urllib
import base64
import logging


def UpdateDomoticz(config, weightdata, bodydata, persondata):
    log = logging.getLogger(__name__)
    domoticzurl = config.get('Domoticz', 'domoticz_url')
    personsection = 'Person' + str(weightdata[0]['person'])
    if config.has_section(personsection):
        weightid = config.get(personsection, 'weight_id')
        weighthid = config.get(personsection, 'weight_hid')
        weightdunit = config.get(personsection, 'weight_dunit')
        fatid = config.get(personsection, 'fat_id')
        kcalid = config.get(personsection, 'kcal_id')
        muscleid = config.get(personsection, 'muscle_id')
        boneid = config.get(personsection, 'bone_id')
        tbwid = config.get(personsection, 'tbw_id')
        bmiid = config.get(personsection, 'bmi_id')
        scaleuser = config.get(personsection, 'username')
        # FIX THIS
        domoticzuser = ""
        domoticzpwd = ""
    else:
        log.error('Unable to update Domoticz: No details found in ini file '
                  'for person %d' % (weightdata[0]['person']))
        return
    try:
        
        def callurl(url, domoticzuser, domoticzpwd):
            log.debug('calling url: %s' % (url))
            try:
                response = urllib.urlopen(url)
            except Exception, e:
                print e
                print url
                log.error('Failed to open url %s' % (url))
            
            #req = urllib2.Request(url)
            #base64string = base64.encodestring('%s:%s' % (
            #           domoticzuser, domoticzpwd)).replace('\n', '')
            #req.add_header('Authorization', 'Basic %s' % base64string)
            #resp = urllib2.urlopen(req)

        """
        log.info('Updating Domoticz for user %s at index %s with bone %s' % (
                  scaleuser, boneid, bodydata[0]['bone']))
        callurl('http://%s/json.htm?type=command&param=udevice&hid=%s&' \
              'did=%s&dunit=%s&dtype=93&dsubtype=1&nvalue=0&svalue=%s' % (
               domoticzurl, weighthid, boneid, weightdunit,
               weightdata[0]['bone']),domoticzuser,domoticzpwd)
        log.info('Updating Domoticz for user %s at index %s with weight %s' % (
                  scaleuser, weightid, weightdata[0]['weight']))
        callurl('http://%s/json.htm?type=command&param=udevice&hid=%s&' \
              'did=%s&dunit=%s&dtype=93&dsubtype=1&nvalue=0&svalue=%s' % (
               domoticzurl, weighthid, weightid, weightdunit,
               weightdata[0]['weight']),domoticzuser,domoticzpwd)
        """

        log.info('Updating Domoticz for user %s at index %s with muscle %s' % (
                  scaleuser, muscleid, bodydata[0]['muscle']))
        callurl('http://%s/json.htm?type=command&param=udevice&idx=%s&nvalue=0&svalue=%s' % (
               domoticzurl, muscleid, bodydata[0]['muscle']),domoticzuser,domoticzpwd)
               
        log.info('Updating Domoticz for user %s at index %s with fat %s' % (
                  scaleuser, fatid, bodydata[0]['fat']))
        callurl('http://%s/json.htm?type=command&param=udevice&idx=%s&nvalue=0&svalue=%s' % (
               domoticzurl, fatid, bodydata[0]['fat']),domoticzuser,domoticzpwd)
               

               
        log.info('Updating Domoticz for user %s at index %s with calories %s' % (
                  scaleuser, kcalid, bodydata[0]['kcal']))
        callurl('http://%s/json.htm?type=command&param=udevice&idx=%s&nvalue=0&svalue=%s' % (
               domoticzurl, kcalid, bodydata[0]['kcal']),domoticzuser,domoticzpwd)
               
        log.info('Updating Domoticz for user %s at index %s with tbw %s' % (
                  scaleuser, tbwid, bodydata[0]['tbw']))
        callurl('http://%s/json.htm?type=command&param=udevice&idx=%s&nvalue=0&svalue=%s' % (
               domoticzurl, tbwid, bodydata[0]['tbw']),domoticzuser,domoticzpwd)

        bmi = 22.0 # weightdata[0]['weight'] / (length * length) # persondata[
        log.info('Updating Domoticz for user %s at index %s with BMI %s' % (
                  scaleuser, bmiid, bodydata[0]['tbw']))
        callurl('http://%s/json.htm?type=command&param=udevice&idx=%s&nvalue=0&svalue=%s' % (
               domoticzurl, bmiid, bmi),domoticzuser,domoticzpwd)

        log.info('Domoticz succesfully updated')
    except Exception, e:
        print str(e)
        

        log.error('Unable to update Domoticz: Error sending data.')
