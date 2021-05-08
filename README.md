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
    }
}
```
##### options.json
```
{
    "paths": {
        "output": "./outputPath"
    }
}
```

and then run the file ```main.py```