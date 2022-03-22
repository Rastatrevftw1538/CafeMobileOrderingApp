import smtplib
from email.mime.text import MIMEText
from email.header import Header

carriers = {
	'att':    '@mms.att.net',
	'tmobile': '@tmomail.net',
	'verizon':  '@vzwpix.com',
	'sprint':   '@page.nextel.com'
}
InfoDict = {}
with open('SecretKeys.txt','r') as Info:
     for line in Info:
          (key,value) = line.split()
          InfoDict[str(key)] = value
def send(message,number):
     to_number = str(number)
     auth = ('cafelouismobileorderapp@gmail.com',InfoDict["SMSTextInfo"])
     msg = MIMEText(str(message),'plain','utf-8')
     msg['Subject'] = Header('Cafe Louis Order Reminder','utf-8')
     msg['From'] = auth[0]
     msg['To'] = to_number
     server = smtplib.SMTP( "smtp.gmail.com", 587 )
     server.ehlo()
     server.starttls()
     server.login(auth[0], auth[1])
     server.sendmail(auth[0], to_number, msg.as_string())
