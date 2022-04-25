import datetime
import discord
import os
import dbutils
import steppingstonegame
from replit import db

DEBUG_MODE = True
client = discord.Client()
botToken = os.environ['TOKEN']
adminId = os.environ['AdminId']
cmdPrefix = '$'
startGameTime = datetime.datetime.now()
endGameTime = datetime.datetime.now()
gameCooldown = datetime.timedelta(minutes=steppingstonegame.gameTime)


# Util functions
def CheckCmd(messageContent, cmd):
    return messageContent.startswith(cmdPrefix + cmd)


# shows when the bot has logged into the server and is ready
@client.event
async def on_ready():
    # current GameInfo version = 0.1
    print(db['GameInfo'])
    if 'GameInfo' not in db.keys():
        print(db.keys())
        db['GameInfo'] = {
            'version': 0.1,
            'StartGameTime': str(datetime.datetime.now()),
            'EndGameTime': str(datetime.datetime.now())
        }
        print(db['GameInfo'])

    global startGameTime
    startGameTime = datetime.datetime.strptime(db['GameInfo']['StartGameTime'],
                                               '%Y-%m-%d %H:%M:%S.%f')

    global endGameTime
    endGameTime = datetime.datetime.strptime(db['GameInfo']['EndGameTime'],
                                             '%Y-%m-%d %H:%M:%S.%f')

    print('We have logged in as {0.user}'.format(client))


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
        else:
            await message.channel.send(authorName + ' already registered!')
        return

    # check if registered before check other cmds
    if authorId not in db.keys():
        await message.channel.send(
            dbutils.MentionAuthor(author) +
            ' please use **$register** to register')
        return

    if not dbutils.CheckVersion(db[authorId]['version']):
        await message.channel.send(
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
            else:
                await message.channel.send(authorName + ' not registered yet!')
            return

        if CheckCmd(messageContent, 'showgame'):
            if steppingstonegame.CheckGame():
                await message.channel.send(db['SteppingStoneGame'])
            else:
                await message.channel.send('No Game Found!')
            return

        if CheckCmd(messageContent, 'showstatus'):
            await steppingstonegame.ShowResult(message, True)
            return

        if CheckCmd(messageContent, 'nukedb'):
            for data in db.keys():
                del db[data]
            return

        if CheckCmd(messageContent, 'current_highscore_reset'):
            for data in db.keys():
                if 'highscore_current' in data.keys():
                    db[data]['highscore_current'] = 0

        if CheckCmd(messageContent, 'force_endgame'):
            if steppingstonegame.EndGame():
                await message.channel.send('Game Ended!')
                await steppingstonegame.ShowResult(message)
            else:
                await message.channel.send('No Game Found!')

    if CheckCmd(messageContent, 'startgame'):
        if currentTime >= startGameTime:
            if steppingstonegame.CheckGame():
                await message.channel.send(
                    'Game running! End game before creating a new one')
            else:
                await message.channel.send('Creating game...')
                steppingstonegame.bIsGameRunning = False

                steppingstonegame.StartGame()
                print(db['SteppingStoneGame'])

                await message.channel.send('Game Created!')
                steppingstonegame.bIsGameRunning = True

                db['GameInfo']['StartGameTime'] = str(datetime.datetime.now() +
                                                      gameCooldown)
        else:
            elapsedTime = startGameTime - currentTime
            await message.channel.send(
                'Game in session for: ' +
                str(int((elapsedTime.seconds % 3600) / 60)) + ' min ' +
                str(elapsedTime.seconds % 60) + ' sec')
        return

    if CheckCmd(messageContent, 'endgame'):
        if currentTime >= startGameTime:
            if steppingstonegame.EndGame():
                await message.channel.send('Game Ended!')
                await steppingstonegame.ShowResult(message)
            else:
                await message.channel.send('No Game Found!')
        else:
            elapsedTime = startGameTime - currentTime
            await message.channel.send(
                'Game in session for: ' +
                str(int((elapsedTime.seconds % 3600) / 60)) + ' min ' +
                str(elapsedTime.seconds % 60) + ' sec')
        return

    if CheckCmd(messageContent, 'update'):
        if dbutils.UpdateRegister(author):
            await message.channel.send(
                dbutils.MentionAuthor(author) + ' updated!')
        else:
            await message.channel.send(
                dbutils.MentionAuthor(author) + ' you are up-to-date!')
        return

    if CheckCmd(messageContent, 'left') or CheckCmd(messageContent, 'right'):
        if steppingstonegame.CheckGame():
            if db[authorId]['is_alive']:
                if CheckCmd(messageContent, 'left'):
                    result = steppingstonegame.Step(authorId, False)
                else:
                    result = steppingstonegame.Step(authorId, True)

                if result == steppingstonegame.StepMessage.Success:
                    await message.channel.send(
                        dbutils.MentionAuthor(author) + ' moved to step ' +
                        str(db[authorId]['current_step']) + '!')
                elif result == steppingstonegame.StepMessage.Fail:
                    occupyingPlayers = ''
                    currentStep = db[authorId]['current_step']

                    for player in db['SteppingStoneGame'][currentStep]:
                        if (player != 'left') and (player != 'right'):
                            occupyingPlayers += (dbutils.MentionId(player) +
                                                 ' ')

                    await message.channel.send(
                        dbutils.MentionAuthor(author) +
                        ' not enough space to go there. Occupied by ' +
                        occupyingPlayers)
                elif result == steppingstonegame.StepMessage.Fell:
                    await message.channel.send(
                        dbutils.MentionAuthor(author) + ' you fell!')
                else:
                    await message.channel.send(
                        dbutils.MentionAuthor(author) + ' INVALID!')
            else:
                await message.channel.send(
                    dbutils.MentionAuthor(author) +
                    ' you are no longer in the game!')
        return

    if CheckCmd(messageContent, 'highscore'):
        await message.channel.send(
            dbutils.MentionAuthor(author) + ' your current highscore is: ' +
            str(dbutils.GetHighscoreCurrent(authorId)) +
            ', your lifetime highscore is: ' +
            str(dbutils.GetHighscoreLifetime(authorId)))
        return

    # test cmd area
    if hasAuthority and CheckCmd(messageContent, 'test'):
        await message.channel.send('Hello ' + dbutils.MentionAuthor(author) +
                                   '!')
        return

    #await message.channel.send('Command not found!')


client.run(botToken)
