import smtplib
import datetime
import mimetypes
import email
import logging


def TimeToString(unixtime):
    returnstr = datetime.datetime.fromtimestamp(unixtime).strftime('%d-%m')
    returnstr += '<br>'
    returnstr += datetime.datetime.fromtimestamp(unixtime).strftime('%H:%M')
    return returnstr


def printcolor(value1, value2, biggerisbetter):
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


def rowdata(header, dataset, property, bib):
    if property == 'timestamp':
        valstr2 = TimeToString(dataset[2][property])
        valstr1 = TimeToString(dataset[1][property])
        valstr0 = TimeToString(dataset[0][property])
        rowstr = '<tr><th>%s</th><th>%s</th><th>%s</th><th>%s</th></tr>' % (
                  header, valstr2, valstr1, valstr0)
    else:
        valstr2 = str(dataset[2][property])
        valstr1 = str(dataset[1][property])
        valstr0 = str(dataset[0][property])
        color1 = printcolor(dataset[1][property], dataset[2][property], bib)
        color0 = printcolor(dataset[0][property], dataset[1][property], bib)
        rowstr = '<tr><td>%s</td><td>%s</td>' \
                 '<td><font color=%s>%s</font></td>' \
                 '<td><font color=%s>%s</font></td></tr>' % (
                  header, valstr2, color1, valstr1, color0, valstr0)
    return rowstr


def BS440mail(config, persondata, weightdata, bodydata):
    log = logging.getLogger(__name__)
    FromAddr = config.get('Email', 'sender_email')
    Password = config.get('Email', 'sender_pwd')
    CcAddr = [config.get('Email', 'sender_email')]
    personsection = 'Person' + str(persondata[0]['person'])
    if config.has_section(personsection):
        ToName = config.get(personsection, 'username')
        ToAddr = [config.get(personsection, 'useremail')]
    else:
        log.error('Unable to send mail: No details found in ini file '
                  'for person %d' % (persondata[0]['person']))
        return
        
    # calculate bmi data list
    calculateddata = []
    size = persondata[0]['size'] / 100.00
    for i in range(0, 3):
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
            <br>
            Groeten,<br>
            Paul.<br>
            </p>
        </body>
    </html>
    """ % (
     ToName,
     rowdata(header='Datum', dataset=weightdata, property='timestamp',
             bib=True),
     rowdata(header='Gewicht (kg)', dataset=weightdata, property='weight',
             bib=False),
     rowdata(header='Vet (%)', dataset=bodydata, property='fat',
             bib=False),
     rowdata(header='Spieren (%)', dataset=bodydata, property='muscle',
             bib=True),
     rowdata(header='Botten (kg)', dataset=bodydata, property='bone',
             bib=True),
     rowdata(header='Water (%)', dataset=bodydata, property='tbw',
             bib=True),
     rowdata(header='Verbruik (kCal)', dataset=bodydata, property='kcal',
             bib=False),
     rowdata(header='BMI', dataset=calculateddata, property='bmi',
             bib=False))

    msg = email.mime.Multipart.MIMEMultipart()
    msg['Subject'] = 'Je nieuwe gewicht'
    msg['From'] = FromAddr
    msg['To'] = ', '.join(ToAddr)
    msg['Cc'] = ', '.join(CcAddr)
    body = email.mime.Text.MIMEText(content, 'html')
    msg.attach(body)
    # send via Gmail server
    log.info('Sending email to ' + ToName + ' at ' + msg['To'])
    try:
        s = smtplib.SMTP('smtp.gmail.com:587')
        s.starttls()
        s.login(FromAddr, Password)
        s.sendmail(FromAddr, ToAddr+CcAddr, msg.as_string())
        s.quit()
        log.info('E-mail successfully sent.')
    except SMTPException:
        log.error('Failed to send e-mail.')
