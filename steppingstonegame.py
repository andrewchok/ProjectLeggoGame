import discord
import enum
import random
import dbutils
from replit import db


# creating enumerations using class
class StepMessage(enum.Enum):
    Success = 0
    Fail = 1
    Fell = 2
    Win = 3
    NoStep = 4


# game settings
maxSteps = 16
maxPlayersOnStep = 2
stepOverhead = 1 #currently just 1 to accommodate bIsBroken
gameTime = 5
gameName = 'SteppingStoneGame'


# Game functions
def IsGameRunning():
    return db['GameInfo']['bIsGameRunning'] 


def SetIsGameRunning(running):
    db['GameInfo']['bIsGameRunning'] = running


def GetCurrentStep(playerinfo):
    return db[playerinfo]['current_step']


def CheckGame():
    bIsInDatabase = gameName in db.keys()
    bIsGameStatusInDatabse = 'GameStatus' in db.keys()
    return IsGameRunning() and bIsInDatabase and bIsGameStatusInDatabse


def AddToGameStatus(player):
    if not db['GameStatus'].count(player):
        db['GameStatus'].append(player)


async def ShowResult(message, debug=False):
    if 'GameStatus' in db.keys():
        #todo: sort by highest step count
        #db['GameStatus'].sort(reverse=True, key=GetCurrentStep)

        outStatus = ''

        if debug:
            outStatus = 'Current Game Status:\n'
        else:
            outStatus = 'End Game Status:\n'

        for player in db['GameStatus']:
            if player != 'ready':
                outStatus = outStatus + dbutils.MentionId(
                    player) + ': step[' + str(
                        db[player]['current_step']) + ']\n'
        await message.channel.send(outStatus)

        if not debug:
            del db['GameStatus']


def EndGame():
    # if there is a game, delete previous game
    if CheckGame():
        del db[gameName]
        SetIsGameRunning(False)
        return True
    return False


def StartGame():
    # create this to hold player info
    db['GameStatus'] = ['ready']

    # get new random seed
    random.seed()
    x = random.randint(1, 100)

    # first step -- ['type of step', bIsBroken]
    if (x > 50):
        db[gameName] = [['right', False]]
    else:
        db[gameName] = [['left', False]]

    # rest of steps
    while len(db[gameName]) < maxSteps:
        x = random.randint(1, 100)
        if (x > 50):
            db[gameName].append(['right', False]) # ['type of step', bIsBroken]
        else:
            db[gameName].append(['left', False]) # ['type of step', bIsBroken]

    # init all players for the game
    for player in db.keys():
        if 'is_alive' in db[player]:
            # set players to alive to play
            db[player]['is_alive'] = True
            # reset players to current step to play
            db[player]['current_step'] = 0


def Step(authorId, bIsRight):
    steps = db[gameName]
    playerInfo = db[authorId]
    currentStep = playerInfo['current_step']
    index_bIsBroken = 1
    

    AddToGameStatus(authorId)

    if currentStep >= maxSteps:
        if authorId in steps[currentStep - 1]:
            steps[currentStep - 1].remove(authorId)
            playerInfo['current_step'] = '*Winner*'
        return StepMessage.Win
      
    # check if step can hold player
    if len(steps[currentStep]) > (maxPlayersOnStep + stepOverhead):
        return StepMessage.Fail

    # remove instance of player from previous step
    if not ((currentStep - 1) < 0):
        if authorId in steps[currentStep - 1]:
            steps[currentStep - 1].remove(authorId)

    if (steps[currentStep][0] == 'left' and not bIsRight) or (steps[currentStep][0] == 'right' and bIsRight):
        # add instance of player to current step
        db[gameName][currentStep].append(authorId)
        playerInfo['current_step'] += 1

        # update current highscore
        if playerInfo['current_step'] > playerInfo['highscore_current']:
            playerInfo['highscore_current'] = playerInfo['current_step']

        # update lifetime highscore
        if playerInfo['highscore_current'] > playerInfo['highscore_lifetime']:
            playerInfo['highscore_lifetime'] = playerInfo['highscore_current'] 

        if currentStep >= maxSteps:
            return StepMessage.Win

        return StepMessage.Success

    else:
        if not db[gameName][currentStep][index_bIsBroken]:
            db[authorId]['is_alive'] = False
            db[gameName][currentStep][index_bIsBroken] = True;
            return StepMessage.Fell
        else:
            return StepMessage.NoStep

