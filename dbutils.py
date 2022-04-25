import discord
from replit import db

# Current Register version: 0.3, added new highscores and push modifiers
registerVersion = 0.3


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
      
    if 'highscore_lifetime' not in db[authorId].keys():
        db[authorId]['highscore_lifetime'] = 0
      
    if 'highscore_current' not in db[authorId].keys():
        db[authorId]['highscore_current'] = 0
      
    if 'highscore' in db[authorId].keys():
        db[authorId]['highscore_lifetime'] = db[authorId]['highscore']
        del db[authorId]['highscore']

    if 'current_step' not in db[authorId].keys():
        db[authorId]['current_step'] = 0
      
    if 'is_alive' not in db[authorId].keys():
        db[authorId]['is_alive'] = False

    if 'pusher_modifier' not in db[authorId].keys():
        db[authorId]['pusher_modifier'] = 0
      
    if 'pushee_modifier' not in db[authorId].keys():
        db[authorId]['pushee_modifier'] = 0

    return True


def CheckVersion(version):
    global registerVersion
    return registerVersion == version


def InitRegister(authorId, authorName):
    db[authorId] = {
        'version': registerVersion,
        'name': authorName,
        'highscore': 0,
        'current_step': 0,
        'is_alive': False,
      # version 0.3
        'highscore_lifetime': 0,
        'highscore_current': 0,
        'pusher_modifier': 0,
        'pushee_modifier': 0
    }


def GetCurrentRegisterVersion():
    return registerVersion

def GetHighscoreCurrent(authorId):
    return db[authorId]['highscore_current']
  
def GetHighscoreLifetime(authorId):
    return db[authorId]['highscore_lifetime']
  
def MentionAuthor(author):
    authorId = str(author.id)
    return '<@' + authorId + '>'

def MentionId(authorId):
    return '<@' + authorId + '>'