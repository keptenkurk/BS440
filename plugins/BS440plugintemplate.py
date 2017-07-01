#-----------------------------------------------------------------------------------------
# BS440 plugin template  BS440template.py
# About:
# [Describe the use of this plugin here] 
#
# Plugin scripts should be named BS440<pluginname>.py
# Any personalization or parameters should be put in BS440<pluginnname>.ini
# Note: The plugin is now an object of class Plugin which affects the way of how
# to declare functions and the way to use them. See BS440mail.py as example
#
# Author: Specify the owner and contact details. Plugins will not be maintained by the
# developer of BS440.py unless specified otherwise.
#
#
#------------------------------------------------------------------------------------------
from ConfigParser import SafeConfigParser
import logging
import os
# Add any imports specific to your plugin here. 
# it is no problem to import modules already imported elsewhere
# if you need them, don't rely on someone else to import them for you.


class Plugin:

    def __init__(self):
        # put any commands here you would like to be run to initialize your plugin
        return
        

    def execute(self, globalconfig, persondata, weightdata, bodydata):
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
        
        '''
        Note that the plugin is now a class.
        As a consequence functions need to be declared as methods, like:
         def mymethod(self, param1, param2)
        
        and be called within the plugin like: 
          result = self.mymethod(var1, var2)
        '''

        # finally end this plugin execution with
        log.info('Finished plugin: ' + __name__)
        
       