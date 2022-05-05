import datetime
import discord
import os
import dbutils
import steppingstonegame
import usercommands
from replit import db

DEBUG_MODE = False
client = discord.Client()
botToken = os.environ['TOKEN']
adminId = os.environ['AdminId']
cmdPrefix = '$'
startGameTime = datetime.datetime.now()
endGameTime = datetime.datetime.now()
gameCooldown = datetime.timedelta(minutes=steppingstonegame.gameTime)
DateTimeAdjust = datetime.timedelta(hours=4)
pushCooldown = datetime.timedelta(minutes=1)


# Util functions
def CheckCmd(messageContent, cmd):
    return messageContent.startswith(cmdPrefix + cmd)


def PrintLog(log):
    logtime = datetime.datetime.now() - DateTimeAdjust
    print('[' + logtime.strftime("%Y-%m-%d %H:%M:%S") + ']: ')
    print(log)


# shows when the bot has logged into the server and is ready
@client.event
async def on_ready():
    # current GameInfo version = 0.2, added bIsGameRunning
    PrintLog(db['GameInfo'])
    if db['GameInfo']['version'] < 0.2:
        PrintLog(db.keys())
        db['GameInfo'] = {
            'version': 0.2,
            'StartGameTime': str(datetime.datetime.now()),
            'EndGameTime': str(datetime.datetime.now()),
            'bIsGameRunning': False
        }
        PrintLog(db['GameInfo'])

    global startGameTime
    startGameTime = datetime.datetime.strptime(db['GameInfo']['StartGameTime'],
                                               '%Y-%m-%d %H:%M:%S.%f')

    global endGameTime
    endGameTime = datetime.datetime.strptime(db['GameInfo']['EndGameTime'],
                                             '%Y-%m-%d %H:%M:%S.%f')

    PrintLog('We have logged in as {0.user}'.format(client))


# reads a message sent
@client.event
async def on_message(message):
    currentTime = datetime.datetime.now()
    global startGameTime
    global endGameTime

    # if message is from Bot early out
    if message.author == client.user:
        return

    # if not a command early out
    if not message.content.startswith(cmdPrefix):
        return

    # declare variable to use
    author = message.author
    authorId = str(message.author.id)
    authorName = str(message.author.name)
    messageContent = message.content.lower()
    hasAuthority = authorId == adminId

    # if in debug mode, do not allow anyone else other than admin to use
    if DEBUG_MODE:
        if not hasAuthority:
            return

    # register a user to the db
    if CheckCmd(messageContent, 'register'):
        if authorId not in db.keys():
            dbutils.InitRegister(authorId, authorName)
            await message.channel.send('Registered: ' + authorName +
                                       ' into the database!')
            PrintLog('Registered: ' + authorName + ' into the database!')
        else:
            await message.channel.send(authorName + ' already registered!')
            PrintLog(authorName + ' already registered!')
        return

    # check if registered before check other cmds
    if authorId not in db.keys():
        await message.channel.send(
            dbutils.MentionAuthor(author) +
            ' please use **$register** to register')
        PrintLog(
            dbutils.MentionAuthor(author) +
            ' please use **$register** to register')
        return

    if CheckCmd(messageContent, 'update'):
        if dbutils.UpdateRegister(author):
            await message.channel.send(
                dbutils.MentionAuthor(author) + ' updated!')
            PrintLog(dbutils.MentionAuthor(author) + ' updated!')
        else:
            await message.channel.send(
                dbutils.MentionAuthor(author) + ' you are up-to-date!')
            PrintLog(dbutils.MentionAuthor(author) + ' you are up-to-date!')
        return

    if not dbutils.CheckVersion(db[authorId]['version']):
        await message.channel.send(
            dbutils.MentionAuthor(author) +
            ' please use **$update** to update your profile')
        PrintLog(
            dbutils.MentionAuthor(author) +
            ' please use **$update** to update your profile')
        return

    if hasAuthority:
        if CheckCmd(messageContent, 'listserverdb'):
            keys = db.keys()
            await message.channel.send(keys)
            return

        if CheckCmd(messageContent, 'listdb'):
            keys = db[authorId].keys()
            await message.channel.send(keys)
            return

        if CheckCmd(messageContent, 'reset'):
            if authorId in db.keys():
                dbutils.InitRegister(authorId, authorName)
                await message.channel.send('Reset: ' + authorName +
                                           ' into the database!')
                PrintLog('Reset: ' + authorName + ' into the database!')
            else:
                await message.channel.send(authorName + ' not registered yet!')
                PrintLog(authorName + ' not registered yet!')
            return

        if CheckCmd(messageContent, 'showgame'):
            if steppingstonegame.CheckGame():
                await message.channel.send(db['SteppingStoneGame'])
                PrintLog(db['SteppingStoneGame'])
            else:
                await message.channel.send('No Game Found!')
                PrintLog('No Game Found!')
            return

        if CheckCmd(messageContent, 'showstatus'):
            await steppingstonegame.ShowResult(message, True)
            return

        if CheckCmd(messageContent, 'nukedb'):
            for data in db.keys():
                del db[data]
            return

        if CheckCmd(messageContent, 'current_scores_reset'):
            for data in db.keys():
                if 'highscore_current' in data.keys():
                    db[data]['highscore_current'] = 0
                if 'wins_current' in data.keys():
                    db[data]['wins_current'] = 0
            return

        if CheckCmd(messageContent, 'force_startgame'):
            if steppingstonegame.CheckGame():
                await message.channel.send(
                    'Game running! End game before creating a new one')
                PrintLog('Game running! End game before creating a new one')
            else:
                await message.channel.send('Creating game...')
                PrintLog('Creating game...')
                steppingstonegame.SetIsGameRunning(False)

                steppingstonegame.StartGame()
                PrintLog(db['SteppingStoneGame'])

                await message.channel.send('Game Created!')
                PrintLog('Game Created!')
                steppingstonegame.SetIsGameRunning(True)

                startGameTime = datetime.datetime.now() + gameCooldown
                db['GameInfo']['StartGameTime'] = str(startGameTime)
            return

        if CheckCmd(messageContent, 'force_endgame'):
            if steppingstonegame.EndGame():
                await message.channel.send('Game Ended!')
                PrintLog('Game Ended!')
                await steppingstonegame.ShowResult(message)

                startGameTime = currentTime
                db['GameInfo']['StartGameTime'] = str(startGameTime)
            else:
                await message.channel.send('No Game Found!')
                PrintLog('No Game Found!')
            return

    if CheckCmd(messageContent, 'startgame'):
        if currentTime >= startGameTime:
            if steppingstonegame.CheckGame():
                await message.channel.send(
                    'Game running! End game before creating a new one')
                PrintLog('Game running! End game before creating a new one')
            else:
                await message.channel.send('Creating game...')
                PrintLog('Creating game...')
                steppingstonegame.SetIsGameRunning(False)

                steppingstonegame.StartGame()
                PrintLog(db['SteppingStoneGame'])

                await message.channel.send('Game Created!')
                PrintLog('Game Created!')
                steppingstonegame.SetIsGameRunning(True)

                startGameTime = datetime.datetime.now() + gameCooldown
                db['GameInfo']['StartGameTime'] = str(startGameTime)
        else:
            elapsedTime = startGameTime - currentTime
            await message.channel.send(
                'Game in session for: ' +
                str(int((elapsedTime.seconds % 3600) / 60)) + ' min ' +
                str(elapsedTime.seconds % 60) + ' sec')
            PrintLog('Game in session for: ' +
                     str(int((elapsedTime.seconds % 3600) / 60)) + ' min ' +
                     str(elapsedTime.seconds % 60) + ' sec')
        return

    if CheckCmd(messageContent, 'endgame'):
        if currentTime >= startGameTime:
            if steppingstonegame.EndGame():
                await message.channel.send('Game Ended!')
                PrintLog('Game Ended!')
                await steppingstonegame.ShowResult(message)

                startGameTime = currentTime
                db['GameInfo']['StartGameTime'] = str(startGameTime)
            else:
                await message.channel.send('No Game Found!')
                PrintLog('No Game Found!')
        else:
            elapsedTime = startGameTime - currentTime
            await message.channel.send(
                'Game in session for: ' +
                str(int((elapsedTime.seconds % 3600) / 60)) + ' min ' +
                str(elapsedTime.seconds % 60) + ' sec')
            PrintLog('Game in session for: ' +
                     str(int((elapsedTime.seconds % 3600) / 60)) + ' min ' +
                     str(elapsedTime.seconds % 60) + ' sec')
        return

    if CheckCmd(messageContent, 'left') or CheckCmd(messageContent, 'right'):
        bIsRight = CheckCmd(messageContent, 'right')
        await usercommands.Command_Step(message, bIsRight)
        return

    if CheckCmd(messageContent, 'highscore'):
        await message.channel.send(
            dbutils.MentionAuthor(author) + ' your current highscore is: **' +
            str(dbutils.GetHighscoreCurrent(authorId)) +
            '**, your lifetime highscore is: **' +
            str(dbutils.GetHighscoreLifetime(authorId)) + '**')
        PrintLog(
            dbutils.MentionAuthor(author) + ' your current highscore is: **' +
            str(dbutils.GetHighscoreCurrent(authorId)) +
            '**, your lifetime highscore is: **' +
            str(dbutils.GetHighscoreLifetime(authorId)) + '**')
        return

    if CheckCmd(messageContent, 'wins'):
        await message.channel.send(
            dbutils.MentionAuthor(author) + ' your current wins is: **' +
            str(dbutils.GetWinsCurrent(authorId)) +
            '**, your lifetime wins is: **' +
            str(dbutils.GetWinsLifetime(authorId)) + '**')
        PrintLog(
            dbutils.MentionAuthor(author) + ' your current wins is: **' +
            str(dbutils.GetWinsCurrent(authorId)) +
            '**, your lifetime wins is: **' +
            str(dbutils.GetWinsLifetime(authorId)) + '**')
        return

    if CheckCmd(messageContent, 'push'):
        currentPushCooldownTime = datetime.datetime.strptime(
            db[authorId]['push_cooldown_time'], '%Y-%m-%d %H:%M:%S.%f')
      
        if currentTime >= currentPushCooldownTime:
            pushOutput = steppingstonegame.Push(authorId)

            pusheeId = pushOutput[0]
            pushMessage = pushOutput[1]
            stepType = pushOutput[2]

            if pushMessage == steppingstonegame.PushMessage.Invalid:
                PrintLog('Error: Push was Invalid, early out')
                return
              
            # not valid  push
            if pushMessage == steppingstonegame.PushMessage.DoNothing:
                await message.channel.send(
                    dbutils.MentionId(authorId) + ' nobody to push!')
                PrintLog(dbutils.MentionId(authorId) + ' nobody to push!')
                return
            
            currentPushCooldownTime = datetime.datetime.now() + pushCooldown
            db[authorId]['push_cooldown_time'] = str(currentPushCooldownTime)
          
            if pushMessage == steppingstonegame.PushMessage.Fail:
                await message.channel.send(
                    dbutils.MentionId(authorId) + ' tried to push ' +
                    dbutils.MentionId(pusheeId) + ' but failed!')
                PrintLog(
                    dbutils.MentionId(authorId) + ' tried to push ' +
                    dbutils.MentionId(pusheeId) + ' but failed!')
                return

            bWasPushed = True
            bPushedToBrokenStep = pushMessage == steppingstonegame.PushMessage.Fell

            await message.channel.send(
                dbutils.MentionId(authorId) + ' pushed ' +
                dbutils.MentionId(pusheeId) + '!')
            PrintLog(
                dbutils.MentionId(authorId) + ' pushed ' +
                dbutils.MentionId(pusheeId) + '!')

            await usercommands.Command_Step(message, stepType == 'right',
                                            pusheeId, bWasPushed,
                                            bPushedToBrokenStep)

        else:
            elapsedTime = currentPushCooldownTime - currentTime
            await message.channel.send(
                dbutils.MentionId(authorId) + ' push on cooldown for: ' +
                str(int((elapsedTime.seconds % 3600) / 60)) + ' min ' +
                str(elapsedTime.seconds % 60) + ' sec')
            PrintLog(
                dbutils.MentionId(authorId) + ' push on cooldown for: ' +
                str(int((elapsedTime.seconds % 3600) / 60)) + ' min ' +
                str(elapsedTime.seconds % 60) + ' sec')
        return

    if CheckCmd(messageContent, 'help'):
        await message.channel.send(
                dbutils.MentionId(authorId) + ' look at the pinned messages for help!')
        return 
      
    # test cmd area
    if hasAuthority and CheckCmd(messageContent, 'test'):
        await message.channel.send('Hello ' + dbutils.MentionAuthor(author) +
                                   '!')
        return
      
    #await message.channel.send('Command not found!')


client.run(botToken)
