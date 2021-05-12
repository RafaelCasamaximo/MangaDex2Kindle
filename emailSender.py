import os

import json

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class EmailSender:

    def __init__(self, body, subject, attachmentList):

        print('Sending files to kindle')

        self.senderAddress = ''
        self.senderPassword = ''
        recieverAddress = ''

        credentials = ''
        with open('credentials.json', 'r') as credentialsFile:
            credentials = json.load(credentialsFile)

        options = ''
        with open('options.json', 'r') as optionsFile:
            options = json.load(optionsFile)


        #The mail addresses and password
        self.senderAddress = credentials['emailLogin']
        self.senderPassword = credentials['emailPassword']
        recieverAddress = options['emailTo']
        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = self.senderAddress
        message['To'] = recieverAddress
        #The subject line
        message['Subject'] = 'A test mail sent by Python. It has an attachment.'

        #Attaching body on the email
        message.attach(MIMEText(body, 'plain'))

        #Attaching documents on the email
        for attachment in attachmentList:
            attachFileName = attachment
            attachFile = open(attachFileName, 'rb') # Open the file as binary mode
            payload = MIMEBase('application', 'octate-stream')
            payload.set_payload((attachFile).read())
            encoders.encode_base64(payload) #encode the attachment
            #add payload header with filename
            payload.add_header('Content-Disposition','attachment; filename="{}"'.format(os.path.basename(attachment)))
            message.attach(payload)


        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security

        #Login with user email and password and then converts and send the message
        session.login(self.senderAddress, self.senderPassword) #login with mail_id and password
        text = message.as_string()
        session.sendmail(self.senderAddress, recieverAddress, text)

        session.quit()
        print('Files sent successfully!')
