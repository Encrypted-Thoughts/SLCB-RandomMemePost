#---------------------------
#   Import Libraries
#---------------------------
import codecs
import json
import os
import re
import sys
import random
import datetime

#---------------------------
#   [Required] Script Information
#---------------------------
ScriptName = "Random Meme Post"
Website = "https://www.twitch.tv/EncryptedThoughts"
Description = "Post a random message and meme to discord using a webhook."
Creator = "EncryptedThoughts"
Version = "1.0.0.0"

#---------------------------
#   Define Global Variables
#---------------------------
SettingsFile = os.path.join(os.path.dirname(__file__), "settings.json")
TimestampFile = os.path.join(os.path.dirname(__file__), "timestamp.json")
ReadMe = os.path.join(os.path.dirname(__file__), "README.txt")
Time = None
StartHour = 8
EndHour = 20

#---------------------------------------
# Classes
#---------------------------------------
class Settings(object):
    def __init__(self, SettingsFile=None):
        if SettingsFile and os.path.isfile(SettingsFile):
            with codecs.open(SettingsFile, encoding="utf-8-sig", mode="r") as f:
                self.__dict__ = json.load(f, encoding="utf-8")
        else:
            self.EnableDebug = True
            self.WebhookUrl = "https://discordapp.com/api/webhooks/YOURWEBHOOK"
            self.Subreddit = "meirl"
            self.PostFormat = "{\"username\":\"Annoy Brandon Bot\",\"content\":\"[MEME_URL]\"}"

    def Reload(self, jsondata):
        self.__dict__ = json.loads(jsondata, encoding="utf-8")

    def Save(self, SettingsFile):
        try:
            with codecs.open(SettingsFile, encoding="utf-8-sig", mode="w+") as f:
                json.dump(self.__dict__, f, encoding="utf-8")
            with codecs.open(SettingsFile.replace("json", "js"), encoding="utf-8-sig", mode="w+") as f:
                f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8')))
        except:
            Parent.Log(ScriptName, "Failed to save settings to file.")
        return

def ReloadSettings(jsonData):
    ScriptSettings.Reload(jsonData)

#---------------------------
#   [Required] Initialize Data (Only called on load)
#---------------------------
def Init():
    global ScriptSettings
    ScriptSettings = Settings(SettingsFile)
    ScriptSettings.Save(SettingsFile)

    global Time
    if os.path.isfile(TimestampFile):
        with open(TimestampFile) as f:
            content = f.readlines()
        Time = datetime.datetime.strptime(content[0], "%Y-%m-%d %H:%M:%S")

    return

#---------------------------
#   [Required] Execute Data / Process messages
#---------------------------
def Execute(data):
    return

#---------------------------
#   [Required] Tick method (Gets called during every iteration even when there is no incoming data)
#---------------------------
def Tick():
    global Time
    if Time is None:
        Time = GetRandomTimestamp(StartHour, EndHour, 0)
        SaveTimestamp()
        if ScriptSettings.EnableDebug:
            Parent.Log(ScriptName, "Updating Time: " + str(Time))

    if Time < datetime.datetime.now():
        if ScriptSettings.EnableDebug:
            Parent.Log(ScriptName, "Sending message: " + str(Time) + " Now: " + str(datetime.datetime.now()))
        data = json.loads(Parent.GetRequest("https://meme-api.herokuapp.com/gimme/" + ScriptSettings.Subreddit, {}))
        if ScriptSettings.EnableDebug:
            Parent.Log(ScriptName, str(data))
        if data["status"] == 200:
            data = json.loads(data["response"])
            send_message(data["url"])
            Time = GetRandomTimestamp(StartHour, EndHour, 1)
            SaveTimestamp()

    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, "Time: " + str(Time) + " Now: " + str(datetime.datetime.now()))

    return

#---------------------------
#   [Optional] Parse method (Allows you to create your own custom $parameters) 
#---------------------------
def Parse(parseString, userid, username, targetid, targetname, message):
    return parseString
#---------------------------
#   [Optional] Unload (Called when a user reloads their scripts or closes the bot / cleanup stuff)
#---------------------------
def Unload():
    return

#---------------------------
#   [Optional] ScriptToggled (Notifies you when a user disables your script or enables it)
#---------------------------
def ScriptToggled(state):
    return

# Explanation on how to obtain a webhook - https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks
# Webhook json formatting example - https://birdie0.github.io/discord-webhooks-guide/discord_webhook.html
def send_message(url): 

    headers = {
      'Content-Type': 'application/json'
    }

    message = ScriptSettings.PostFormat.replace("[MEME_URL]", url)

    result = Parent.PostRequest(ScriptSettings.WebhookUrl,headers,json.loads(message), True)
  
    if ScriptSettings.EnableDebug:
        Parent.Log(ScriptName, result)

    return result

def openreadme():
    os.startfile(ReadMe)

def openjson():
    os.startfile("https://codebeautify.org/jsonviewer?input=" + ScriptSettings.PostFormat)

def SaveTimestamp():
    with open(TimestampFile, 'w') as f:
        f.write(str(Time))

def GetRandomTimestamp(start, end, dayOffset):
    now = datetime.datetime.now() + datetime.timedelta(days=dayOffset)
    startDate = datetime.datetime(now.year, now.month, now.day, start, now.minute, now.second)
    endDate = datetime.datetime(now.year, now.month, now.day, end, now.minute, now.second)
    return startDate + datetime.timedelta(
        seconds=random.randint(0, int((endDate - startDate).total_seconds())),
    )