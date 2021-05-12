# MangaDex2Kindle
---
#### A script made for automatically download your unread chapters from MangaDex and sending them to your 

#### Running
In order to run the script you have to manually set 2 files:

##### credentials.json
```
{
    "username": "yourUsername",
    "password": "yourPassword",
    "token": {
        "session": "null",
        "refresh": "null"
    },
    "emailLogin": "yourAddress@mail.com",
    "emailPassword": "yourPassword"
}
```
##### options.json
```
{
    "paths": {
        "output": "./outputPath"
    },
    "emailTo": "yourAddress@Kindle.com"
}
```

##### Why these variables and files?

In order to prevent the program to ask you for different inputs the script uses different JSON files to get the data. Feel free to clone this repo and make use of it. But remember to NOT upload your credentials while doing it.

and then run the file ```main.py``` with ```python main.py```

#### Dependencies

```click``` - For the CLI (WIP) 
```calibre``` - Tool used to make the conversion to ```.html``` to ```.mobi```