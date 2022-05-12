import discord
import datetime
from replit import db

# Current Register version: 0.8, add revive via phoenixdown
registerVersion = 0.8


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

    if 'wins_lifetime' not in db[authorId].keys():
        db[authorId]['wins_lifetime'] = 0

    if 'wins_current' not in db[authorId].keys():
        db[authorId]['wins_current'] = 0
    
    if 'push_cooldown_time' not in db[authorId].keys():
        db[authorId]['push_cooldown_time'] = str(datetime.datetime.now())

    if 'push_cooldown_time' in db[authorId].keys():
        db[authorId]['push_cooldown_time'] = str(datetime.datetime.now())
    
    if 'phoenixdown_cooldown_time' not in db[authorId].keys():
        db[authorId]['phoenixdown_cooldown_time'] = str(datetime.datetime.now())

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
        'pushee_modifier': 0,
        # version 0.4
        'wins_lifetime': 0,
        'wins_current': 0,
        # version 0.5, 0.6, 0.7
        'push_cooldown_time': str(datetime.datetime.now()),
        # version 0.8
        'phoenixdown_cooldown_time': str(datetime.datetime.now())
    }
    # remember to update the UpdateRegister() with new value


def GetCurrentRegisterVersion():
    return registerVersion


def GetHighscoreCurrent(authorId):
    return db[authorId]['highscore_current']


def GetHighscoreLifetime(authorId):
    return db[authorId]['highscore_lifetime']


def GetWinsCurrent(authorId):
    return db[authorId]['wins_current']


def GetWinsLifetime(authorId):
    return db[authorId]['wins_lifetime']


def MentionAuthor(author):
    authorId = str(author.id)
    return '<@' + authorId + '>'


def MentionId(authorId):
    return '<@' + authorId + '>'
