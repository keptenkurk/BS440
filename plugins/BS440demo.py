#-----------------------------------------------------------------------------------------
# BS440 plugin template  BS440template.py
# About:
# [Describe the use of this plugin here] 
#
# Plugin scripts should be named BS440<pluginname>.py
# Any personalization or parameters should be put in BS440<pluginnname>.ini
#
# Author: Specify the owner and contact details. Plugins will not be maintained by the
# developer of BS440.py unless specified otherwise.
#
#
#------------------------------------------------------------------------------------------

# put the imports specific to our plugin here. 
# it is no problem to import modules already imported elsewhere
# if you need them, don't rely on someone else to import them for you.
import [modulesrequired]


class Plugin:

    def __init__(self):
        # put any commands here you would like to be run to initialize your plugin
        return
        

    def execute(self, globalconfig, persondata, weightdata, bodydata):
        # your plugin receives the config details from BS440.ini as well as
        # all the data received frm the scale
        # enable logging
        log = logging.getLogger(__name__)
        # read the ini file specific to this plugin
        config = SafeConfigParser()
        config.read(__name__ + '.ini')
        # Thats it! From here do your thing with the data.
        # Be sure to catch and log errors if you're doing risky stuff