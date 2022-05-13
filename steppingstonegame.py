import datetime
import discord
import enum
import random
import dbutils
from replit import db

DateTimeAdjust = datetime.timedelta(hours=4)


def PrintLog(log):
    logtime = datetime.datetime.now() - DateTimeAdjust
    print('[' + logtime.strftime("%Y-%m-%d %H:%M:%S") + ']: ')
    print(log)


# creating enumerations using class
class StepMessage(enum.Enum):
    Success = 0
    Fail = 1
    Fell = 2
    Win = 3
    NoStep = 4


class PushMessage(enum.Enum):
    Invalid = -1
    Success = 0
    Fail = 1
    Fell = 2
    DoNothing = 4


# game settings
maxSteps = 16
maxPlayersOnStep = 2
stepOverhead = 1  #currently just 1 to accommodate bIsBroken
gameTime = 5  # time in minutes
gameName = 'SteppingStoneGame'


# Game functions
def IsGameRunning():
    return db['GameInfo']['bIsGameRunning']


def SetIsGameRunning(running):
    db['GameInfo']['bIsGameRunning'] = running


def GetCurrentStep(playerinfo):
    return db[playerinfo]['current_step']


def CheckGame():
    global gameName

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
    global gameName

    # if there is a game, delete previous game
    if CheckGame():
        del db[gameName]
        SetIsGameRunning(False)
        return True
    return False


def StartGame():
    global gameName

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
            db[gameName].append(['right',
                                 False])  # ['type of step', bIsBroken]
        else:
            db[gameName].append(['left', False])  # ['type of step', bIsBroken]

    # init all players for the game
    for player in db.keys():
        if 'is_alive' in db[player]:
            # set players to alive to play
            db[player]['is_alive'] = True
            # reset players to current step to play
            db[player]['current_step'] = 0


def Step(authorId, bIsRight, bWasPushed=False, bPushedToBrokenStep=False):
    global stepOverhead
    global maxPlayersOnStep
    global maxSteps
    global gameName

    steps = db[gameName]
    playerInfo = db[authorId]
    currentStep = playerInfo[
        'current_step']  #this is the step player is going to
    index_bIsBroken = 1

    AddToGameStatus(authorId)

    if currentStep >= maxSteps:
        if authorId in steps[currentStep - 1]:
            steps[currentStep - 1].remove(authorId)
            playerInfo['current_step'] = '*Winner*'

            # update current wins
            playerInfo['wins_current'] = playerInfo['wins_current'] + 1

            # update lifetime wins
            playerInfo['wins_lifetime'] = playerInfo['wins_lifetime'] + 1

        return StepMessage.Win

    # check if step can hold player, ignore if being pushed
    if len(steps[currentStep]) > (maxPlayersOnStep + stepOverhead) and (
            not bPushedToBrokenStep):
        return StepMessage.Fail

    # remove instance of player from previous step
    if not ((currentStep - 1) < 0):
        if authorId in steps[currentStep - 1]:
            steps[currentStep - 1].remove(authorId)

    if ((steps[currentStep][0] == 'left' and not bIsRight) or
        (steps[currentStep][0] == 'right'
         and bIsRight)) and (not bPushedToBrokenStep):
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
        if not db[gameName][currentStep][index_bIsBroken] or bWasPushed:
            db[authorId]['is_alive'] = False
            db[gameName][currentStep][index_bIsBroken] = True
            return StepMessage.Fell
        else:
            return StepMessage.NoStep


def RollChance():
    # roll a d20, if 10 or above it successful and returns true
    roll = random.randint(1, 20)
    PrintLog('RollChance: rolled a ' + str(roll))
    return roll >= 10


def Push(authorId):
    global stepOverhead
    global maxSteps
    global gameName

    output = ['', PushMessage.Invalid, '']
    steps = db[gameName]
    pusherInfo = db[authorId]
    pusheeId = ''
    currentStep = pusherInfo['current_step']
    index_bIsBroken = 1
    index_PusheeId = 0
    index_PushMessage = 1
    index_StepType = 2
    pushOverhead = 2  # +1 step type, and +1 player(pusher)
    pusheeArr = ['temp']

    # if player is not alive, do nothing
    if not db[authorId]['is_alive']:
        output[index_PushMessage] = PushMessage.DoNothing
        return output

    # if player is on the other side, do nothing
    if currentStep >= maxSteps:
        output[index_PushMessage] = PushMessage.DoNothing
        return output

    # check if other players on same step
    if len(steps[currentStep - 1]) > (stepOverhead + pushOverhead):
        # get other players on same step
        for key in steps[currentStep - 1]:
            # make sure all key checking is strings
            tempKey = str(key)
            if tempKey != authorId and tempKey != 'True' and tempKey != 'False' and tempKey != 'left' and tempKey != 'right':
                if pusheeArr[0] == 'temp':
                    pusheeArr[0] = tempKey
                else:
                    pusheeArr.append(tempKey)

        # choose a random player to push
        randPusheeIndex = random.randint(0, len(pusheeArr) - 1)
        output[index_PusheeId] = pusheeArr[randPusheeIndex]

        # if the step being pushed to has a broken step, then pusher wants to eliminate pushee
        if db[gameName][currentStep][index_bIsBroken]:
            # do roll checks
            if (RollChance()):
                output[index_PushMessage] = PushMessage.Fell
            else:
                output[index_PushMessage] = PushMessage.Fail

            return output

        # if the step being pushed to has max ppl already, then pusher wants to eliminate pushee
        if currentStep >= 0 and currentStep < len(steps):
            if len(steps[currentStep]) > (maxPlayersOnStep + stepOverhead):
                # do roll checks
                if (RollChance()):
                    output[index_PushMessage] = PushMessage.Fell
                else:
                    output[index_PushMessage] = PushMessage.Fail
                return output

        # push to a random step in front
        randStepChoice = random.randint(1, 100)

        if (randStepChoice > 50):  #right
            output[index_StepType] = 'right'
        else:  #left
            output[index_StepType] = 'left'

        # do roll checks
        if (RollChance()):
            output[index_PushMessage] = PushMessage.Success
        else:
            output[index_PushMessage] = PushMessage.Fail

        return output

    # fail safe return
    return output
