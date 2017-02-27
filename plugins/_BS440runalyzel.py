# -----------------------------------------------------------------------------------------
# BS440 Runalyze local plugin  BS440runalyzel.py
# About:
# Inserts last weighing into local Runalyze database
#
# Personalization or parameters can be put in BS440runalyze.ini
#
# Author: genlinut
#
# ------------------------------------------------------------------------------------------
from ConfigParser import SafeConfigParser
import logging
import os
import MySQLdb


class Plugin:

    def __init__(self):
        # put any commands here you would like to be run to initialize your plugin
        return

    def execute(self, globalconfig, persondata, weightdata, bodydata):
        # --- part of plugin skeleton
        # your plugin receives the config details from BS440.ini as well as
        # all the data received from the scale
        log = logging.getLogger(__name__)
        log.info('Starting plugin: ' + __name__)
        # read ini file from same location as plugin resides, named [pluginname].ini
        configfile = os.path.dirname(os.path.realpath(__file__)) + '/' + __name__ + '.ini'
        pluginconfig = SafeConfigParser()
        pluginconfig.read(configfile)
        log.info('ini read from: ' + configfile)
        # Thats it! From here do your thing with the data.

        personsection = 'Person' + str(weightdata[0]['person'])
        scaleuser = pluginconfig.get(personsection, 'username')
        runalyzeID = pluginconfig.get(personsection, 'runalyzeID')

        sql_host = pluginconfig.get('RunalyzeLocal', 'host')
        sql_user = pluginconfig.get('RunalyzeLocal', 'user')
        sql_passwd = pluginconfig.get('RunalyzeLocal', 'passwd')
        sql_db = pluginconfig.get('RunalyzeLocal', 'db')

        log.info("Updating Runalyze per SQL-Query for user %s (ID %s)" % (scaleuser, runalyzeID))

        try:
            db = MySQLdb.connect(sql_host, sql_user, sql_passwd, sql_db)
            cur = db.cursor()
            sql_cmd = ("INSERT INTO runalyze_user (time, weight, fat, water, muscles, accountid) VALUES"
                       "('%s', '%s', '%s', '%s', '%s', '%s')" % (
                        weightdata[0]['timestamp'],
                        weightdata[0]['weight'],
                        bodydata[0]['fat'],
                        bodydata[0]['tbw'],
                        bodydata[0]['muscle'],
                        runalyzeID))
            log.info(sql_cmd)
            a = cur.execute(sql_cmd)
            cur.close()
            db.commit()
            db.close()
            log.info('Update successful!')
        except:
            log.error('Unable to update Runalyze per SQL-Query: Error sending data.')

        # finally end this plugin execution with
        log.info('Finished plugin: ' + __name__)
