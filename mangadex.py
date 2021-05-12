import os
import os.path
from os import path
from datetime import datetime
import json
import requests
import click
from fnmatch import fnmatch
import ntpath

from emailSender import EmailSender

class Mangadex:
    def __init__(self):

        #Attributes
        self.followedMangaList = ''
        self.newChaptersSortedByMangas = []

        credentialsFile = open('credentials.json')
        self.credentials = json.load(credentialsFile)
        self.hed = {'Authorization': 'Bearer ' + self.credentials['token']['session']}


        #Makes a connection with the mangadex
        self.connect()

        #Get a list of the user followed mangas
        self.getFollowedMangaFeed()
        
        #Iterate the list of followed mangas 
        for manga in self.followedMangaList['results']:

            #Get the chapter list of a manga
            chaptersList = self.getChaptersFromManga(manga, ['en'])

            #Get the ID of the readed chapters of a manga
            readedChaptersIdList = self.getReadedChaptersIdFromManga(manga)

            #Get the not readed chapters list
            notReadedChapters = self.getNotReadedChapters(chaptersList, readedChaptersIdList)

            #This method updates the 'newChaptersSortedByMangas' attribute with data about the manga and the chapters not readed in it
            self.updateNewChaptersSortedByMangas(manga, notReadedChapters)

        #Creates a log file about the new chapters and mangas releases for the user
        log = self.createDailyLog(self.newChaptersSortedByMangas)
        #Iterate over the 'newChaptersSortedByMangas' attribute to download every new chapter from every manga followed
        self.downloadUpdates(self.newChaptersSortedByMangas)

        attachFiles = []

        os.chdir('..')

        for file in os.listdir('./output/mobiOutputs/'):
            attachFiles.append('./output/mobiOutputs/' + file)

        

        emailTeste = EmailSender()
        emailTeste.createNewEmail(log, 'Daily Updates - MangaDex')
        emailTeste.attachFiles(attachFiles)
        emailTeste.send()



    """
    This method try to connect with the best way possible. Always trying to connect through tokens first instead of generating a new one every time
    """
    def connect(self):

        if self.credentials['token']['session'] != 'null':
            #Tenta checar o token já existente
            #Try connection with a existing token
            response = requests.get('https://api.mangadex.org/auth/check', headers=self.hed)
            response = response.json()

            if response['isAuthenticated'] == True:
                self.hed = {'Authorization': 'Bearer ' + self.credentials['token']['session']}
                print('Connection made with existent token!')
                return
            
            #Tenta um refresh do token
            #Try connection refreshing the token
            params = {
                'token': self.credentials['token']['session']
            }
            response = requests.get('https://api.mangadex.org/auth/refresh', headers=self.hed)
            
            if response.status_code == 200:
                response = response.json()

                self.credentials.update({
                    "token": response['token']
                })

                with open('credentials.json', 'w') as credentialsFile:
                    json.dump(self.credentials, credentialsFile)

                self.hed = {'Authorization': 'Bearer ' + self.credentials['token']['session']}
                print('Connection made with refresh token!')
                return


        #Realiza o login com as credenciais de username e password
        #Try connection using the credentials username and password
        params = {
            'username': self.credentials['username'],
            'password': self.credentials['password']
        }

        try:
            response = requests.post('https://api.mangadex.org/auth/login', json=params)

            if response.status_code == 200:
                response = response.json()

                self.credentials.update({
                    "token": response['token']
                })

                with open('credentials.json', 'w') as credentialsFile:
                    json.dump(self.credentials, credentialsFile)

                self.hed = {'Authorization': 'Bearer ' + self.credentials['token']['session']}
                print('Connection made with new token!')
                return

        except:
            print('Connection to Mangadex dennied!')
            quit()

    """
    Gets the list of the mangas followed by the user logged
    """
    def getFollowedMangaFeed(self):

        #Get my Followed manga list 
        response = requests.get('https://api.mangadex.org/user/follows/manga', headers=self.hed)
        response = response.json()
        self.followedMangaList = response

        with open('data.json', 'w') as dataFile:
            json.dump(response, dataFile)



        """
        Pegar uma lista de mangas que eu dou follow

        Para cada manga que eu dou follow eu tenho que pegar duas coisas
        -Todos os capitulos lançados até agora (no maximo 100 por conta da paginação)
        -Todos os capitulos marcados como lidos

        Após isso, tenho que gerar uma nova lista com os capitulos não lidos até então
        """

    """
    Gets a list of the chapters from a specified manga object
    """
    def getChaptersFromManga(self, manga, locales = ['null']):
        mangaId = manga['data']['id']

        params = {}

        if locales != ['null']:
            params.update({
                'locales[]': locales,
                'order[chapter]': 'desc',
                'order[volume]': 'desc'
            })

        response = requests.get('https://api.mangadex.org/manga/{}/feed'.format(mangaId), params=params, headers=self.hed)
        response = response.json()

        with open('chapterList.json', 'w') as dataFile:
            json.dump(response, dataFile)


        return response

    """
    Gets a list of ids from the readed chapters from a specified manga object
    """
    def getReadedChaptersIdFromManga(self, manga):
        mangaId = manga['data']['id']

        response = requests.get('https://api.mangadex.org/manga/{}/read'.format(mangaId), headers=self.hed)
        response = response.json()

        with open('chapterIdList.json', 'w') as dataFile:
            json.dump(response, dataFile)

        return response

    """
    Use the list of chapters from a specified manga and the list of the readed chapters ids to make a list of unreaded chapters
    """
    def getNotReadedChapters(self, chaptersList, readedChaptersIdList):
        notReadedChapters = []

        #Thats a test while the API don't support del or put methods. I'm manually removing a chapter id from the 'readed chapters list'
        readedChaptersIdList['data'].remove('42c910b9-0432-4a70-b455-bd10e366b47f')
        

        for chapter in chaptersList['results']:
            chapterId = chapter['data']['id']
            if chapterId not in readedChaptersIdList['data']:
                notReadedChapters.append(chapter)
        
        with open('notReadedChaptersList.json', 'w') as dataFile:
            json.dump(notReadedChapters, dataFile)

        return notReadedChapters

    """
    Makes a array of objects:
    [
        {
            'manga': {'title: string', 'status': string},
            'chapters': {chapterObject} (from mangadex)
        },
        {...}
    ]
    save as attribute 'newChaptersSortedByMangas'
    """
    def updateNewChaptersSortedByMangas(self, manga, notReadedChapters):

        update = {
            'manga': {
                'title': manga['data']['attributes']['title']['en'],
                'status': manga['data']['attributes']['status']
            },
            'chapters': notReadedChapters,
        }

        self.newChaptersSortedByMangas.append(update)

        with open('dailyUpdates.json', 'w') as dataFile:
            json.dump(self.newChaptersSortedByMangas, dataFile)

    """
    Creates a daily log of the new chapters released from the followed mangas
    """
    def createDailyLog(self, newChaptersSortedByMangas):

        #Go to output folder
        options = ''
        with open('options.json') as optionsFile:
            options = json.load(optionsFile)
        if path.isdir(options['paths']['output']):
            os.chdir(options['paths']['output'])
        else:
            os.mkdir(options['paths']['output'])
            os.chdir(options['paths']['output'])


        now = datetime.now()

        logContent = ''

        with open(now.strftime('%d-%m-%Y-%H-%M-%S') + '-log.txt', 'w') as logFile:
            for updates in newChaptersSortedByMangas:
                logContent += 'Manga Title: \'' + updates['manga']['title'] + '\'\n'
                for newChapter in updates['chapters']:
                    logContent += '\t' + newChapter['data']['attributes']['chapter'] + ': \'' + newChapter['data']['attributes']['title'] + '\'\n'
            
            logFile.write(logContent)

        os.chdir('..')
        
        return logContent


    """
    Downloads new chapters from manga that the user follows that are marked as unread
    Iterates over the updatesList to make that
    """
    def downloadUpdates(self, newChaptersSortedByMangas):

        #Go to output folder
        options = ''
        with open('options.json') as optionsFile:
            options = json.load(optionsFile)

        os.chdir(options['paths']['output'])

        #iterate over newChaptersSortedByMangas
        for update in newChaptersSortedByMangas:
            print('Downloading [' + update['manga']['title'] + '] chapters:')
            if path.isdir(update['manga']['title']):
                os.chdir(update['manga']['title'])
            else:
                os.mkdir(update['manga']['title'])
                os.chdir(update['manga']['title'])

            #Iterates over chapters
            for chapter in update['chapters']:

                #Go to chapter folder
                print('\tDownloading chapter [{}]'.format(chapter['data']['attributes']['chapter']))
                if path.isdir('[' + chapter['data']['attributes']['chapter'] + '] - ' + update['manga']['title'] + ': ' + chapter['data']['attributes']['title']):
                    os.chdir('[' + chapter['data']['attributes']['chapter'] + '] - ' + update['manga']['title'] + ': ' + chapter['data']['attributes']['title'])
                else:
                    os.mkdir('[' + chapter['data']['attributes']['chapter'] + '] - ' + update['manga']['title'] + ': ' + chapter['data']['attributes']['title'])
                    os.chdir('[' + chapter['data']['attributes']['chapter'] + '] - ' + update['manga']['title'] + ': ' + chapter['data']['attributes']['title'])

                #Generate the images list for download
                chapterPages = []

                #TODO make the server request 
                for imageLink in chapter['data']['attributes']['data']:
                    chapterPages.append('https://s2.mangadex.org/data/{}/{}'.format(chapter['data']['attributes']['hash'], imageLink))
                
                self.downloadArrayOfImages(chapterPages)

                self.makeHtmlChapter(update['manga']['title'], chapter['data']['attributes']['chapter'], chapter['data']['attributes']['title'])

                os.chdir('..')

            os.chdir('..')

            print('Converting chapters to .mobi')

            if not path.isdir('mobiOutputs'):
                os.mkdir('mobiOutputs')

            htmlFilesList = self.getAllFilesFromTypeInSubdir(os.getcwd(), '*.html')
            
            for htmlFile in htmlFilesList:
                chapterName = self.pathLeaf(htmlFile)
                os.system('ebook-convert \'{}\' \'{}\' --output-profile kindle_pw3 --margin-bottom 0 --margin-left 0 --margin-right 0 --margin-top 0 --remove-paragraph-spacing >/dev/null 2>&1'.format(htmlFile, os.path.join('mobiOutputs', chapterName.replace('html', 'mobi'))))
            
    
    """
    This method takes a array of URLs as parameter and then downloads them in the current folder
    """
    def downloadArrayOfImages(self, images):
        for idx, img in enumerate(images):
            response = requests.get(img, stream=True)
            if response.status_code == 200:
                with open(str(idx).zfill(4) + '.jpg', 'wb') as imageFile:
                    for chunk in response:
                        imageFile.write(chunk)

    """
    This method makes an HTML for a chapter with the parameters using the images on the current folder
    """
    def makeHtmlChapter(self, mangaTitle, chapterNumber, chapterTitle):

        #Make sure to only use the image files in case of rerunning the code 
        imageList = os.listdir('./')
        for image in imageList:
            if not image.endswith(".jpg"):
                imageList.remove(image)

        #To make images always in asc. order
        imageList.sort()
        mangaContent = ''
        for image in imageList:
            mangaContent += '<img src=\"' + image + '\" height="90%" />\n'

        #Makes an HTML template for each chapter
        htmlContent = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>[''' + chapterNumber + '''] - ''' + mangaTitle + ''' : ''' + chapterTitle + '''</title>
        </head>
        <body>
            ''' + mangaContent + '''
        </body>
        </html>
        '''

        with open('[{chapterNumber}] - {mangaTitle}: {chapterTitle}.html'.format(chapterNumber=chapterNumber, mangaTitle=mangaTitle, chapterTitle=chapterTitle), 'w') as htmlChapterFile:
            htmlChapterFile.write(htmlContent)

    """
    This util function gets all files from a type on directory and subdirectory and return them in a list
    """
    def getAllFilesFromTypeInSubdir(self, root, pattern):
        filesList = []

        for path, subdirs, files in os.walk(root):
            for name in files:
                if fnmatch(name, pattern):
                    filesList.append(os.path.join(path, name))
        
        return filesList

    """
    This function extracts the name of a file in a path
    """
    def pathLeaf(self, path):
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)