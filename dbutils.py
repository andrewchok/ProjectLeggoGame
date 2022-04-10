import discord
from replit import db

# Current Register version: 0.2
registerVersion = 0.2


def UpdateRegister(author):
    authorId = str(author.id)

    if 'version' in db[authorId].keys():
        if db[authorId]['version'] == registerVersion:
            return False
        else:
            db[authorId]['version'] = registerVersion
            db[authorId]['name'] = str(author.name)

    if 'version' not in db[authorId].keys():
        db[authorId]['version'] = registerVersion
        db[authorId]['name'] = str(author.name)

    if 'highscore' not in db[authorId].keys():
        db[authorId]['highscore'] = 0

    if 'current_step' not in db[authorId].keys():
        db[authorId]['current_step'] = 0
      
    if 'is_alive' not in db[authorId].keys():
        db[authorId]['is_alive'] = False

    return True


def CheckVersion(version):
    return registerVersion == version


def InitRegister(authorId, authorName):
    db[authorId] = {
        'version': registerVersion,
        'name': authorName,
        'highscore': 0,
        'current_step': 0,
        'is_alive': False
    }


def GetCurrentRegisterVersion():
    return registerVersion


def GetHighscore(authorId):
    return db[authorId]['highscore']

def MentionAuthor(author):
    authorId = str(author.id)
    return '<@' + authorId + '>'

def MentionId(authorId):
    return '<@' + authorId + '>'