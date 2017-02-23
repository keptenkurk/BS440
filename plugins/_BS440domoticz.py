#-----------------------------------------------------------------------------------------
# BS440 plugin BS440domoticz.py
# About:
# Updates scae values to virtual sensors in Domoticz Home automation system 
#
# Uses BS440domoticz.ini for plugin parameters
#
# Author: Tristan79
#
#------------------------------------------------------------------------------------------
from ConfigParser import *
import os
import urllib
import base64
import logging
import time
import traceback
import json

__author__ = 'Tristan79'


class Plugin:

    def __init__(self):
        # put any commands here you would like to be run to initialize your plugin
        return


    def open_url(self, url):
        log.debug('Opening url: %s' % (url))
        try:
            response = urllib.urlopen(url)
        except Exception, e:
            log.error('Failed to send data to Domoticz (%s)' % (url))
            return 'None'
        return response


    def exists_hardware(self, name):
        response = self.open_url(url_hardware % (domoticzurl))
        if response == 'None':
            return 'None'
        data = json.loads(response.read())
        if 'result' in data:
            for i in range(0,len(data['result'])):
                if name == data['result'][i]['Name']:
                    return data['result'][i]['idx']
        return 'None'
        
        
    def rename_sensors(self, sensorid,name):
        try:
            response = self.open_url(url_sensor_ren % (domoticzurl,sensorid,name))
        except:
            pass


    def exists_sensor(self, name):
        global query
        global data
        if query:
            response = self.open_url(url_sensor % (domoticzurl))
            if response == 'None':
                return 'None'
            data = json.loads(response.read())
            query = False
        if 'result' in data:
            for i in range(0,len(data['result'])):
                if name == data['result'][i]['Name'] and int(hardwareid) == data['result'][i]['HardwareID']:
                    return data['result'][i]['idx']
        return 'None'


    def self.exists_id(self, sensorid):
        global query
        global data
        if query:
            response = self.open_url(url_sensor % (domoticzurl))
            if response == 'None':
                return False
            data = json.loads(response.read())
            query = False
        if 'result' in data:
            for i in range(0,len(data['result'])):
                if sensorid == data['result'][i]['idx'] and int(hardwareid) == data['result'][i]['HardwareID']:
                    return True
        return False


    def exists_realid(self, realid):
        global query
        global data
        if query:
            response = self.open_url(url_sensor % (domoticzurl))
            if response == 'None':
                return ["",""]
            data = json.loads(response.read())
            query = False
        if 'result' in data:
            for i in range(0,len(data['result'])):
                if str(realid) == data['result'][i]['ID'] and int(hardwareid) == data['result'][i]['HardwareID']:
                    return [data['result'][i]['idx'],data['result'][i]['Name']]
        return ["",""]


    def rename_realid(self, id, newname):
        global query
        query = True
        d = self.exists_realid(id)
        if d[1] == "Unknown":
            self.rename_sensors(d[0],newname)
            query = True


    def use_virtual_sensor(self, name, type, options=''):
        global query
        sensorid = self.exists_sensor(name)
        if 'None' != sensorid:
            return sensorid
        if 'None' == sensorid:
            url = url_sensor_add % (domoticzurl, hardwareid, name.replace(' ', '%20'),str(type))
            if options != '':
                url = url + '&sensoroptions=' + options
            response = self.open_url(url)
            query = True
            return self.exists_sensor(name)


    # create or discover sensors
    def get_id(self, iniid, text, type, options=""):
        try:
            rid = pluginpluginconfig.get(personsection, iniid)
            if not self.exists_id(id):
                raise Exception
        except:
            rid = self.use_virtual_sensor(user + ' ' + text,type,options)
            pluginconfig.set(personsection, iniid, rid)
            write_config = True
        return rid
        

    def get_realid(self, iniid,default):
        try:
            return pluginpluginconfig.get(personsection, iniid)
        except:
            write_config = True
            pluginconfig.set(personsection, iniid, str(default))
            return default
                

    def execute(self, globalconfig, persondata, weightdata, bodydata):
        # --- part of plugin skeleton
        # your plugin receives the config details from BS440.ini as well as
        # all the data received from the scale
        log = logging.getLogger(__name__)
        log.info('Starting plugin: ' + __name__)
        #read ini file from same location as plugin resides, named [pluginname].ini
        configfile = os.path.dirname(os.path.realpath(__file__)) + '/' + __name__ + '.ini'
        pluginconfig = SafeConfigParser()
        pluginconfig.read(configfile)
        log.info('ini read from: ' + configfile)


        write_config = False
        data = '{}'
        query = True
        SensorPercentage = 2
        SensorCustom     = 1004

        domoticzurl = pluginconfig.get('Domoticz', 'domoticz_url')     
        try:
            hardwarename = pluginconfig.get('Domoticz', 'hardware_name')
        except:
            hardwarename = "Medisana"

        domoticzuser = ""
        domoticzpwd = ""
      
        # read user's name 
        personsection = 'Person' + str(weightdata[0]['person'])
        if config.has_section(personsection):
            user = pluginconfig.get(personsection, 'username')
        else:
            log.error('Unable to update Domoticz: No details found in ini file '
                      'for person %d' % (weightdata[0]['person']))
            return
        
        url_mass = 'http://%s/json.htm?type=command&param=udevice&hid=%s&' \
                  'did=%s&dunit=%s&dtype=93&dsubtype=1&nvalue=0&svalue=%s'
        url_per = 'http://%s/json.htm?type=command&param=udevice&idx=%s&nvalue=0&svalue=%s'
        url_hardware_add = 'http://%s/json.htm?type=command&param=addhardware&htype=15&port=1&name=%s&enabled=true'
        url_hardware = 'http://%s/json.htm?type=hardware'
        url_sensor = 'http://%s/json.htm?type=devices&filter=utility&order=Name'
        url_sensor_add = 'http://%s/json.htm?type=createvirtualsensor&idx=%s&sensorname=%s&sensortype=%s'
        url_sensor_ren = 'http://%s/json.htm?type=command&param=renamedevice&idx=%s&name=%s'

 
        # Check if hardware exists and add if not..
        hardwareid = self.exists_hardware(hardwarename)
        if 'None' == hardwareid:
            response = self.open_url(url_hardware_add % (domoticzurl, hardwarename.replace(' ', '%20')))
            hardwareid = self.exists_hardware(hardwarename)
            if 'None' == hardwareid:
                log.error('Unable to access or create Domoticz hardware')
                return

        try:
            try:
                pluginconfig.add_section(personsection)
            except DuplicateSectionError:
                pass
            fatid = self.get_id('fat_per_id','Fat Percentage',SensorPercentage)
            bmrid = self.get_id('bmr_id','BMR',SensorCustom,'1;Calories')
            muscleid = self.get_id('muscle_per_id','Muscle Percentage',SensorPercentage)
            boneid = self.get_id('bone_per_id','Bone Percentage',SensorPercentage)
            waterid = self.get_id('water_per_id','Water Percentage',SensorPercentage)
            lbmperid = self.get_id('lbm_per_id','Water Percentage',SensorPercentage)
            bmiid = self.get_id('bmi_id','BMI',SensorCustom,'1;')
            
            # Mass
            weightid = self.get_realid('weight_id',79)
            fatmassid = self.get_realid('fat_mass_id',80)
            watermassid = self.get_realid('watermass_id',81)
            musclemassid = self.get_realid('muscle_mass_id',82)
            bonemassid = self.get_realid('bone_mass_id',83)
            lbmid = self.get_realid('lbm_id',84)
            weightunit = self.get_realid('weight_unit',1)
            fatmassunit = self.get_realid('fatmass_unit',1)
            watermassunit = self.get_realid('watermass_unit',1)
            musclemassunit = self.get_realid('musclemass_unit',1)
            bonemassunit = self.get_realid('bonemass_unit',1)
            lbmunit = self.get_realid('lbm_unit',1)
            
        except:
            log.error('Unable to access Domoticz sensors')
            return

        write_config = True

        #### ----gaat dit goed? configfile vs fconfigfile
        if write_config:
            with open(configfile, 'wb') as fconfigfile:
                pluginconfig.write(configfile)
                configfile.close()
                write_config = False

        try:
            # calculate and populate variables
            weight = weightdata[0]['weight']
            fat_per = bodydata[0]['fat']
            fat_mass = weight * (fat_per / 100.0)
            water_per = bodydata[0]['tbw']
            water_mass = weight * (water_per / 100.0)
            muscle_per = bodydata[0]['muscle']
            muscle_mass = (muscle_per / 100) * weight
            bone_mass = bodydata[0]['bone']
            bone_per = (bone_mass / weight) * 100
            lbm = weight - (weight * (fat_per / 100.0))
            lbm_per = (lbm / weight) * 100
            kcal = bodydata[0]['kcal']
            bmi = 0
            for p in persondata:
                if p['person'] == bodydata[0]['person']:
                    size = p['size'] / 100.0
                    bmi = weight / (size * size)

            log_update = 'Updating Domoticz for user %s at index %s with '

            # Mass

            log.info((log_update+'weight %s') % (user, weightid, weight))
            self.open_url(url_mass % (domoticzurl, hardwareid, weightid, weightunit, weight))

            log.info((log_update+'fat mass %s') % (user, fatmassid, fat_mass))
            self.open_url(url_mass % (domoticzurl, hardwareid, fatmassid, fatmassunit, fat_mass))

            log.info((log_update+'water mass %s') % (user, watermassid, water_mass))
            self.open_url(url_mass % (domoticzurl, hardwareid, watermassid, watermassunit, water_mass))

            log.info((log_update+'muscle mass %s') % (user, musclemassid, muscle_mass))
            self.open_url(url_mass % (domoticzurl, hardwareid, musclemassid, musclemassunit, muscle_mass))

            log.info((log_update+'bone mass %s') % (user, bonemassid, bone_mass))
            self.open_url(url_mass % (domoticzurl, hardwareid, bonemassid, bonemassunit, bone_mass))

            log.info((log_update+'lean body mass %s') % (user, lbmid, lbm))
            self.open_url(url_mass % (domoticzurl, hardwareid, lbmid, lbmunit, lbm))

            # Percentage

            log.info((log_update+'fat percentage %s') % (user, fatid, fat_per))
            self.open_url(url_per % (domoticzurl, fatid, fat_per))

            log.info((log_update+'water percentage %s') % (user, waterid, water_per))
            self.open_url(url_per % (domoticzurl, waterid, water_per))
                   
            log.info((log_update+'muscle percentage %s') % (user, muscleid, muscle_per))
            self.open_url(url_per % (domoticzurl, muscleid, muscle_per))

            log.info((log_update+'bone percentage %s') % (user, boneid, bone_per))
            self.open_url(url_per % (domoticzurl, boneid, bone_per))

            log.info((log_update+'lean body mass percentage %s') % (user, lbmperid, lbm_per))
            self.open_url(url_per % (domoticzurl, lbmperid, lbm_per))
            
            # Other

            log.info((log_update+'basal metabolic rate calories %s') % (user, bmrid, kcal))
            self.open_url(url_per  % (domoticzurl, bmrid, kcal))
                
            log.info((log_update+'body mass index %s') % (user, bmiid, bmi))
            self.open_url(url_per  % (domoticzurl, bmiid, bmi))

            self.rename_realid(weightid,user + " " + 'Weight')
            self.rename_realid(fatmassid,user + " " + 'Fat Mass')
            self.rename_realid(musclemassid,user + " " + 'Muscle Mass')
            self.rename_realid(watermassid,user + " " + 'Water Mass')
            self.rename_realid(bonemassid,user + " " + 'Bone Mass')
            self.rename_realid(lbmid,user + " " + 'Lean Body Mass')

            log.info('Domoticz succesfully updated')

        except:
            log.error('Unable to update Domoticz: Error sending data.')
