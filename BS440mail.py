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


def BS440mail(config, persondata, weightdata, bodydata):
    log = logging.getLogger(__name__)
    FromAddr = config.get('Program', 'sender_email')
    Password = config.get('Program', 'sender_pwd')
    CcAddr = [config.get('Program', 'sender_email')]

    personsection = 'Person' + str(persondata[0]['person'])
    if config.has_section(personsection):
        ToName = config.get(personsection, 'username')
        ToAddr = [config.get(personsection, 'useremail')]
    else:
        log.error('Unable to send mail: No details found in ini file for person %d' % (persondata[0]['person']))
        return

    # Sort scale output to retrieve most recent three results
    wds = sorted(weightdata, key=lambda k: k['timestamp'], reverse=True)
    bds = sorted(bodydata, key=lambda k: k['timestamp'], reverse=True)

    # Build HTML e-mail content
    content = """
    <html>
        <html>
            <head>
            <style>
            table {
                width:100%;
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
            <p>Beste """ + ToName + """<br>
            Je hebt zojuist op de weegschaal gestaan. Dit is een overzicht van je laatste 3 metingen:<br>
            <br>
            <table id="t01">
              <tr>
                <th>Datum</th>
                <th>""" + TimeToString(wds[2]['timestamp']) + """</th>
                <th>""" + TimeToString(wds[1]['timestamp']) + """</th>
                <th>""" + TimeToString(wds[0]['timestamp']) + """</th>
              </tr>
              <tr>
                <td>Gewicht (kg)</td>
                <td>""" + str(wds[2]['weight']) + """</td>
                <td>""" + str(wds[1]['weight']) + """</td>
                <td>""" + str(wds[0]['weight']) + """</td>
              </tr>
              <tr>
                <td>Vet (%)</td>
                <td>""" + str(bds[2]['fat']) + """</td>
                <td>""" + str(bds[1]['fat']) + """</td>
                <td>""" + str(bds[0]['fat']) + """</td>
              </tr>
              <tr>
                <td>Spieren (%)</td>
                <td>""" + str(bds[2]['muscle']) + """</td>
                <td>""" + str(bds[1]['muscle']) + """</td>
                <td>""" + str(bds[0]['muscle']) + """</td>
              </tr>
              <tr>
                <td>Botten (kg)</td>
                <td>""" + str(bds[2]['bone']) + """</td>
                <td>""" + str(bds[1]['bone']) + """</td>
                <td>""" + str(bds[0]['bone']) + """</td>
              </tr>
              <tr>
                <td>Water (%)</td>
                <td>""" + str(bds[2]['tbw']) + """</td>
                <td>""" + str(bds[1]['tbw']) + """</td>
                <td>""" + str(bds[0]['tbw']) + """</td>
              </tr>
              <tr>
                <td>Verbruik (kcal)</td>
                <td>""" + str(bds[2]['kcal']) + """</td>
                <td>""" + str(bds[1]['kcal']) + """</td>
                <td>""" + str(bds[0]['kcal']) + """</td>
              </tr>
            </table>
            <br>
            <br>
            Groeten,<br>
            Paul.<br>
            </p>
        </body>
    </html>
    """
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
