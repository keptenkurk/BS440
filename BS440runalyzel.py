import logging
import MySQLdb

def UpdateRunalyzeLocal(config, persondata, weightdata, bodydata):
    log = logging.getLogger(__name__)
    personsection = 'Person' + str(weightdata[0]['person'])
    scaleuser = config.get(personsection, 'username')
    runalyzeID = config.get(personsection, 'runalyzeID')
    
    sql_host = config.get('RunalyzeLocal', 'host')
    sql_user = config.get('RunalyzeLocal', 'user')
    sql_passwd = config.get('RunalyzeLocal', 'passwd')
    sql_db = config.get('RunalyzeLocal', 'db')
    
    log.info('Updating Runalyze per SQL-Query for user %s (ID %s) with weight %s, fat %s, water %s  and muscle: %s' %
             (scaleuser, runalyzeID, weightdata[0]['weight'], bodydata[0]['fat'], bodydata[0]['tbw'], bodydata[0]['muscle']))

    try:
        db=MySQLdb.connect(sql_host, sql_user, sql_passwd, sql_db)
        
        cur=db.cursor()

        log.info("INSERT INTO runalyze_user (time, weight, fat, water, muscles, accountid) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (weightdata[0]['timestamp'], weightdata[0]['weight'], bodydata[0]['fat'], bodydata[0]['tbw'], bodydata[0]['muscle'], runalyzeID))

        a=cur.execute("INSERT INTO runalyze_user (time, weight, fat, water, muscles, accountid) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (weightdata[0]['timestamp'], weightdata[0]['weight'], bodydata[0]['fat'], bodydata[0]['tbw'], bodydata[0]['muscle'], runalyzeID))

        cur.close()
        db.commit()
        db.close()

        log.info('Update successful!')
    except:
        log.error('Unable to update Runalyze per SQL-Query: Error sending data.')
