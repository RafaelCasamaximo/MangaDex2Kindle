import os

import json

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

"""
EmailSender
createNewEmail
attachFiles
send
"""

class EmailSender:

    def __init__(self):

        #Attributes for a new email
        self.senderAddress = ''
        self.senderPassword = ''
        self.recieverAddress = ''
        self.message = ''

        credentials = ''
        with open('credentials.json', 'r') as credentialsFile:
            credentials = json.load(credentialsFile)


        #The mail addresses and password
        self.senderAddress = credentials['emailLogin']
        self.senderPassword = credentials['emailPassword']

    def createNewEmail(self, body, subject):

        options = ''
        with open('options.json', 'r') as optionsFile:
            options = json.load(optionsFile)

        self.recieverAddress = options['emailTo']

        print('Setting E-mail')
        #Setup the MIME
        self.message = MIMEMultipart()
        self.message['From'] = self.senderAddress
        self.message['To'] = self.recieverAddress
        #The subject line
        self.message['Subject'] = subject

        #Attaching body on the email
        self.message.attach(MIMEText(body, 'plain'))

    def attachFiles(self, attachmentList):
        print('Attaching files on the E-mail')
        #Attaching documents on the email
        for idx, attachment in enumerate(attachmentList):
            print('Attaching file {}/{}'.format(idx, len(attachmentList)))
            attachFileName = attachment
            attachFile = open(attachFileName, 'rb') # Open the file as binary mode
            payload = MIMEBase('application', 'octate-stream')
            payload.set_payload((attachFile).read())
            encoders.encode_base64(payload) #encode the attachment
            #add payload header with filename
            payload.add_header('Content-Disposition','attachment; filename="{}"'.format(os.path.basename(attachment)))
            self.message.attach(payload)

        print('All attachments done successfully')


    def send(self):
        print('Sending the E-mail')
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security

        #Login with user email and password and then converts and send the message
        session.login(self.senderAddress, self.senderPassword) #login with mail_id and password
        text = self.message.as_string()
        session.sendmail(self.senderAddress, self.recieverAddress, text)

        session.quit()
        print('E-mail sent successfully')
