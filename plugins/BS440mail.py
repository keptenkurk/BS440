import smtplib
import datetime
import mimetypes
import email
import logging
from ConfigParser import SafeConfigParser
import os
import random


class Plugin:

    def __init__(self):
        return
        
        
    def TimeToString(self, unixtime):
        returnstr = datetime.datetime.fromtimestamp(unixtime).strftime('%d-%m')
        returnstr += '<br>'
        returnstr += datetime.datetime.fromtimestamp(unixtime).strftime('%H:%M')
        return returnstr


    def printcolor(self, value1, value2, biggerisbetter):
        black = '000000'
        red = 'FF0000'
        green = '00FF00'
        if value1 == value2:
            color = black
        if value1 > value2:
            if biggerisbetter:
                color = green
            else:
                color = red
        if value1 < value2:
            if biggerisbetter:
                color = red
            else:
                color = green
        return color

    def praise(self, praisefilename, dataset):
        praisestr = ''
        # open praises file if any
        if praisefilename != '':
            try:
                praisefile = open(praisefilename, "r")
                # select aproriate praises
                valstr3 = dataset[3]['weight']
                valstr2 = dataset[2]['weight']
                valstr1 = dataset[1]['weight']
                valstr0 = dataset[0]['weight']
                selectstr = '---'
                selectlst = list(selectstr)
                if valstr2 > valstr3: selectlst[0] = '+'
                if valstr1 > valstr2: selectlst[1] = '+'
                if valstr0 > valstr1: selectlst[2] = '+'
                selectstr = ''.join(selectlst)
                praiselines = []
                for line in praisefile:
                    if line[0:3] == selectstr:
                        praiselines.append(line[3:])
                if len(praiselines)>0:
                    praisestr = praiselines[random.randint(0,len(praiselines)-1)]
            except IOError:
                praisestr = ''
        return praisestr

        
    def rowdata(self, header, dataset, property, bib):
        if property == 'timestamp':
            valstr2 = self.TimeToString(dataset[2][property])
            valstr1 = self.TimeToString(dataset[1][property])
            valstr0 = self.TimeToString(dataset[0][property])
            rowstr = '<tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>' % (
                      header, valstr2, valstr1, valstr0)
        else:
            valstr3 = dataset[3][property]
            valstr2 = dataset[2][property]
            valstr1 = dataset[1][property]
            valstr0 = dataset[0][property]
            color2 = self.printcolor(dataset[2][property], dataset[3][property], bib)
            color1 = self.printcolor(dataset[1][property], dataset[2][property], bib)
            color0 = self.printcolor(dataset[0][property], dataset[1][property], bib)
            rowstr = '<tr><td>%s</td>' \
                     '<td><font color=%s>%s</font></td>' \
                     '<td><font color=%s>%s</font></td>' \
                     '<td><font color=%s>%s</font></td></tr>' % (
                      header, color2, valstr2, color1, valstr1, color0, valstr0)
        return rowstr


    def execute(self, config, persondata, weightdata, bodydata):

        # --- part of plugin skeleton
        log = logging.getLogger(__name__)
        log.info('Starting plugin: ' + __name__)
        #read ini file from same location as plugin resides, named [pluginname].ini
        configfile = os.path.dirname(os.path.realpath(__file__)) + '/' + __name__ + '.ini'
        pluginconfig = SafeConfigParser()
        pluginconfig.read(configfile)
        log.info('ini read from: ' + configfile)
        
        # --- start plugin specifics here

        if pluginconfig.has_option('Email', 'smtp_server'):
            SmtpServer = pluginconfig.get('Email', 'smtp_server')
        else:
            SmtpServer = ''
        if pluginconfig.has_option('Email', 'start_tls'):
            StartTls = pluginconfig.getboolean('Email', 'start_tls')
        else:
            StartTls = False
        FromAddr = pluginconfig.get('Email', 'sender')
        if pluginconfig.has_option('Email', 'login'):
            Login = pluginconfig.get('Email', 'login')
        else:
            Login = False
        if pluginconfig.has_option('Email', 'password'):
            Password = pluginconfig.get('Email', 'password')
        else:
            Password = False
        CcAddr = [pluginconfig.get('Email', 'sender')]
        personsection = 'Person' + str(persondata[0]['person'])
        if pluginconfig.has_section(personsection):
            ToName = pluginconfig.get(personsection, 'username')
            ToAddr = [pluginconfig.get(personsection, 'useremail')]
            if pluginconfig.has_option(personsection, 'Praises'):
                praisefilename = pluginconfig.get(personsection, 'Praises')
            else:
                praisefilename = '' 
        else:
            log.error('Unable to send mail: No details found in ini file '
                      'for person %d' % (persondata[0]['person']))
            return
            
        # calculate bmi data list
        calculateddata = []
        size = persondata[0]['size'] / 100.00
        for i in range(0, 4):
            bmiDict = {}
            bmiDict['bmi'] = round(weightdata[i]['weight'] / (size * size), 1)
            calculateddata.append(bmiDict)


        # Build HTML e-mail content
        content = """
        <html>
            <html>
                <head>
                <style>
                table {
                    width:100%%;
                }
                table, th, td {
                    border: 1px solid black;
                    border-collapse: collapse;
                }
                th, td {
                    padding: 5px;
                    text-align: right;
                }
                table#t01 tr:nth-child(even) {
                    background-color: #eee;
                }
                table#t01 tr:nth-child(odd) {
                   background-color:#fff;
                }
                table#t01 th	{
                    background-color: black;
                    color: white;
                }
                </style>
                </head>
                <body>
                <p>Beste %s<br>
                Je hebt zojuist op de weegschaal gestaan.<br>
                Dit is een overzicht van je laatste 3 metingen:<br>
                <br>
                <table id="t01">%s%s%s%s%s%s%s%s
                </table>
                <br>
                %s<br>
                Groeten,<br>
                De weegschaal.<br>
                </p>
            </body>
        </html>
        """ % (
         ToName,
         self.rowdata(header='Datum', dataset=weightdata, property='timestamp',
                 bib=True),
         self.rowdata(header='Gewicht (kg)', dataset=weightdata, property='weight',
                 bib=False),
         self.rowdata(header='Vet (%)', dataset=bodydata, property='fat',
                 bib=False),
         self.rowdata(header='Spieren (%)', dataset=bodydata, property='muscle',
                 bib=True),
         self.rowdata(header='Botten (kg)', dataset=bodydata, property='bone',
                 bib=True),
         self.rowdata(header='Water (%)', dataset=bodydata, property='tbw',
                 bib=True),
         self.rowdata(header='Verbruik (kCal)', dataset=bodydata, property='kcal',
                 bib=False),
         self.rowdata(header='BMI', dataset=calculateddata, property='bmi',
                 bib=False),
         self.praise(praisefilename, dataset=weightdata))

        msg = email.mime.Multipart.MIMEMultipart()
        msg['Subject'] = 'Je nieuwe gewicht'
        msg['From'] = FromAddr
        msg['To'] = ', '.join(ToAddr)
        msg['Cc'] = ', '.join(CcAddr)
        body = email.mime.Text.MIMEText(content, 'html')
        msg.attach(body)
        # send via smtp server
        log.info('Sending email to ' + ToName + ' at ' + msg['To'])
        try:
            s = smtplib.SMTP(SmtpServer)
            if StartTls:
                s.starttls()
            if Login and Password:
                s.login(Login, Password)

            s.sendmail(FromAddr, ToAddr+CcAddr, msg.as_string())
            s.quit()
            log.info('E-mail successfully sent.')
        except smtplib.SMTPException as e:
            log.error('Failed to send e-mail:')
            log.error(e)

        log.info('Finished plugin: ' + __name__)
