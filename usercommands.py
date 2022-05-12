import datetime
import discord
import os
import dbutils
import steppingstonegame
import usercommands
import random
import requests
import json
from replit import db

tenorToken = os.environ['TENOR_TOKEN']
cmdPrefix = '$'
DateTimeAdjust = datetime.timedelta(hours=4)


def CheckCmd(messageContent, cmd):
    return messageContent.startswith(cmdPrefix + cmd)


def PrintLog(log):
    logtime = datetime.datetime.now() - DateTimeAdjust
    print('[' + logtime.strftime("%Y-%m-%d %H:%M:%S") + ']: ')
    print(log)


async def SendFallGIF(message):
    # set the apikey and limit
    apikey = tenorToken  # test value
    lmt = 24

    # our test search
    search_term = "fall down"

    # get the top 12 GIFs for the search term
    r = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" %
                     (search_term, apikey, lmt))

    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        top_8gifs = json.loads(r.content)

        # get the GIF's id and search used
        randGif = random.randint(0, lmt - 1)
        shard_gifs_id = top_8gifs['results'][randGif]["id"]

        r = requests.get(
            "https://g.tenor.com/v1/registershare?id=%s&key=%s&q=%s" %
            (shard_gifs_id, apikey, search_term))

        if r.status_code == 200:
            pass
            # move on
            await message.channel.send(top_8gifs['results'][randGif]["url"])
        else:
            pass
            # handle error
    else:
        top_8gifs = None


async def Command_Step(message,
                       bIsRight,
                       PusheeId='',
                       bWasPushed=False,
                       bPushedToBrokenStep=False):
    # declare variable to use
    author = message.author
    playerId = ''
    messageContent = message.content.lower()

    if PusheeId != '':
        playerId = PusheeId
    else:
        playerId = str(message.author.id)

    if steppingstonegame.CheckGame():
        if db[playerId]['is_alive']:
            result = steppingstonegame.Step(playerId, bIsRight, bWasPushed,
                                            bPushedToBrokenStep)

            if result == steppingstonegame.StepMessage.Success:
                await message.channel.send(
                    dbutils.MentionId(playerId) + ' moved to step ' +
                    str(db[playerId]['current_step']) + '!')
                PrintLog(
                    dbutils.MentionId(playerId) + ' moved to step ' +
                    str(db[playerId]['current_step']) + '!')
            elif result == steppingstonegame.StepMessage.Fail:
                occupyingPlayers = ''
                currentStep = db[playerId]['current_step']

                for player in db['SteppingStoneGame'][currentStep]:
                    if (player != 'left') and (player != 'right') and (
                            str(player) != "True") and (str(player) !=
                                                        "False"):
                        occupyingPlayers += (dbutils.MentionId(player) + ' ')

                await message.channel.send(
                    dbutils.MentionId(playerId) +
                    ' not enough space to go there. Occupied by ' +
                    occupyingPlayers)
                PrintLog(
                    dbutils.MentionId(playerId) +
                    ' not enough space to go there. Occupied by ' +
                    occupyingPlayers)
            elif result == steppingstonegame.StepMessage.Fell:
                await message.channel.send(
                    dbutils.MentionId(playerId) + ' you fell!')
                await SendFallGIF(message)
                PrintLog(dbutils.MentionId(playerId) + ' you fell!')
            elif result == steppingstonegame.StepMessage.Win:
                await message.channel.send(
                    dbutils.MentionId(playerId) +
                    ' you made it to the other side!')
                PrintLog(
                    dbutils.MentionId(playerId) +
                    ' you made it to the other side!')
            elif result == steppingstonegame.StepMessage.NoStep:
                await message.channel.send(
                    dbutils.MentionId(playerId) + ' that step is broken!')
                PrintLog(dbutils.MentionId(playerId) + ' that step is broken!')
            else:
                await message.channel.send(
                    dbutils.MentionId(playerId) + ' INVALID!')
                PrintLog(dbutils.MentionId(playerId) + ' INVALID!')
        else:
            await message.channel.send(
                dbutils.MentionId(playerId) +
                ' you are no longer in the game!')
            PrintLog(
                dbutils.MentionId(playerId) +
                ' you are no longer in the game!')
