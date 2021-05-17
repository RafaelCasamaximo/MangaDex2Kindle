import os
import json
from typing import Dict

from MangaDexPy import MangaDex


class MangaDexKindle:
    """Program to get MangaDex user feed, download the new chapters and send to the user's kindle"""

    def __init__(self, path: str = './json', settingsFile: str = 'settings.json') -> None:

        # Attributes
        self.cli = MangaDex()
        self.path = path
        self.settingsFile = settingsFile
        self.settings = ''

        self._load_settings()

    def _load_settings(self, path: str = './json', settingsPath: str = 'settings.json') -> None:
        # Check if folder exists
        if not os.path.isdir(path):
            os.mkdir(path)
            print('Creating dir ' + path)

        # Check if file exists
        settingsFilePath = os.path.join(path, settingsPath)
        if not os.path.isfile(settingsFilePath):

            print('-First Time Login:')
            username = input('Mangadex Username: ')
            password = input('Mangadex Password: ')

            settings = {
                'mangadexCredentials': {
                    'username': username,
                    'password': password,
                    'token': None
                }
            }

            self.settings = settings
            print('Creating file ' + settingsPath)
            with open(settingsFilePath, 'w') as settingsFile:
                json.dump(settings, settingsFile, indent=4)

        # Load settings from existent file
        else:
            print('Loading Settings from existent file.')
            with open(settingsFilePath, 'r') as settingsFile:
                self.settings = json.load(settingsFile)

        isConnected = False
        if not self.settings['mangadexCredentials']['token'] == None:
            self.cli.session_token = self.settings['mangadexCredentials']['token']['session']
            self.cli.refresh_token = self.settings['mangadexCredentials']['token']['refresh']
            self.cli.session.headers['Authorization'] = self.cli.session_token
            isConnected = self.cli.check()
            if isConnected:
                print('Current token still valid.')
                return isConnected
        if not isConnected:
            print('Generating and saving new token with new login.')
            isConnected = self.cli.login(self.settings['mangadexCredentials']['username'],
                                         self.settings['mangadexCredentials']['password'])
            if isConnected:
                self.settings['mangadexCredentials']['token'] = {
                    'session': self.cli.session_token, 'refresh': self.cli.refresh_token}

                with open(settingsFilePath, 'w') as settingsFile:
                    json.dump(self.settings, settingsFile, indent=4)

                print('New token generated.')
                return isConnected

        print('Could not make login.')
        return False
