import os
import json
from typing import Dict

from MangaDexPy import MangaDex


class MangaDexKindle:
    """Program to get MangaDex user feed, download the new chapters and send to the user's kindle"""

    def __init__(self, jsonPath: str = './json', settingsFile: str = 'settings.json') -> None:

        # Attributes
        self.jsonPath = jsonPath
        self.settingsFile = settingsFile
        self.settings = ''

        # Load credentials and check if it exists
        if self._check_file(self.jsonPath, self.settingsFile):
            self.settings = self._load_settings()
        if not self._check_folder(self.jsonPath):
            os.mkdir(self.jsonPath)
        if not self._check_file(self.jsonPath, settingsFile):
            self._save_settings()

    def _load_settings(self) -> Dict:
        """Load settings from jsonPath/settings.json"""
        settingsPath = os.path.join(self.jsonPath, self.settingsFile)
        with open(settingsPath, 'r') as settingsFile:
            return json.load(settingsFile)

    def _save_settings(self) -> None:
        """Save settings in jsonPath/settings.json"""
        settingsPath = os.path.join(self.jsonPath, self.settingsFile)
        settings = {
            'mangadexCredentials': {
                'username': None,
                'password': None,
                'token': None
            }
        }
        with open(settingsPath, 'w') as settingsFile:
            json.dump(settings, settingsFile, indent=4)

    def _check_file(self, baseDir: str, file: str) -> bool:
        path = os.path.join(baseDir, file)
        return os.path.isfile(path)

    def _check_folder(self, dir) -> bool:
        return os.path.isdir(dir)
