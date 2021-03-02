# Work with Python 3.6
# -*- coding: iso-8859-1 -*-
import discord
import json
from PIL import Image
from discord.ext import commands
import os
import time

with open ("token.txt", "r") as myfile:
    TOKEN=myfile.readlines()[0]
helpResponse = ['']
helpResponse.append("")
with open ("README.md", "r") as myfile:
    helpResponseTmp=myfile.readlines()
    indexCurr = 0;
    for i in range(0, len(helpResponseTmp)):
        if(len(helpResponse[indexCurr]) + len(helpResponseTmp[i]) > 1000):
            helpResponse.append(helpResponseTmp[i])
            indexCurr +=1
        else: 
            helpResponse[indexCurr] += helpResponseTmp[i]
            
client =  commands.Bot(command_prefix='!')
nationsToTag = {}
tagToNations = {}
tagToPixel = {}
guildsToTime = {}       #set min waiting time to 0 so it does nothing atm
activeOnGuild = {}

gamemodes = {"!1444":"eu4_normal", "!includeVassals": "eu4_VassalsInc", "!vic2": "vic2_normal", "!hoi4": "hoi4_normal", "!100Dev": "100Dev_normal"}

with open('data.json') as json_file:
    tagToNations = json.load(json_file)
for tag in tagToNations.keys():
    for nation in tagToNations[tag][0]:
        nationsToTag[nation] = tag
    nationsToTag[tag] = tag
    
    tagToPixel[tag] = [tagToNations[tag][1],tagToNations[tag][2]]
    
async def getReservedNations(channel):
    nations = {}
    async for message in channel.history(limit=200):
        split = message.content.lower().split("\n")
        for line in split:
            if line.startswith("!reserve ") and line.split(" ")[1] in nationsToTag:
                nations[nationsToTag[line.split(" ")[1]]] = [tagToPixel[nationsToTag[line.split(" ")[1]]], line.split(" ")[2]]
            nation = line if " " not in line else line.split(" ")[0].lower()   #ignore everything after whitespace
            nation = nation if "(" not in nation else nation.split("(")[0]                                              #ignore everything after (
            authorName = message.author.nick if (hasattr(message.author, 'nick') and message.author.nick != None) else message.author.name
            if nation in nationsToTag.keys():
                nations[nationsToTag[nation]] = [tagToPixel[nationsToTag[nation]], authorName]
        
    return nations
    
async def getInvalidMessages(channel):
    messages = {}
    async for message in channel.history(limit=200):
        if message.author == client.user:
            continue
        nation = message.content.lower() if " " not in message.content else message.content.split(" ")[0].lower()   #ignore everything after whitespace
        nation = nation if "(" not in nation else nation.split("(")[0]           
        if nation not in nationsToTag.keys() and nation not in tagToPixel.keys() and not message.content.startswith("!"):
            messages[message] = 1
        
    return messages
        
def getColoredMap(nations, gamemode):
    
    im = Image.open("images/"+ gamemode.split("_")[0] + "_mapWorld.png")
    width, height = im.size
    pixels = im.load()
    colors = {(68,107,163):1}                                       #dont overwrite water/borders
    for nation in nations:
        if nations[nation][0][0]==0 and nations[nation][0][1] == 0:
            print("skipping "+ nation)
            continue
        if(nations[nation][0][0]>5600 or nations[nation][0][1] > 2000): 
            print("error nation: " + str(nation))
            continue                                                #i sometimes write wrong coords into data.json :(
        colors[pixels[nations[nation][0][0],nations[nation][0][1]]] = 1
    print(colors)
    
    im = Image.open("images/" + gamemode + "_map.png")
    pixels = im.load()
    width, height = im.size
    for i in range(0, width): 
        for j in range(0, height): 
            color = pixels[i, j]
            if  ((not (color==(68,107,163))) and ((((i+1) < width) and not (pixels[i+1, j] == color) and (color in colors.keys() or pixels[i+1,j] in colors.keys())) or 
                    (((j+1) < height) and not (pixels[i, j+1] == color) and (color in colors.keys() or pixels[i,j+1] in colors.keys())))):
                pixels[i, j] = (0,0,0)
            elif pixels[i, j] not in colors.keys():
                pixels[i,j] = (127,127,127)
    return im
    
def createReservationsString(nations):
    reservationsStr = "**Total Players: " + str(len(nations)) + "**\n" 
    nationsArr = [0]*len(nations)
    i = 0
    for n in nations.keys():
        nationsArr[i] = tagToNations[n][0][0] + " : " + str(nations[n][1])
        i+=1
    nationsArr.sort()
    for i in range(0,len(nationsArr)):
        reservationsStr += "\n" + nationsArr[i]
    print(reservationsStr.encode('utf-8', 'replace'))
    return reservationsStr
    
async def updateMap(message, reservationsChannel, reservationMapChannel, gamemode = "eu4_VassalsInc"):
    print(gamemode)
    checkedForOldMessage = False
    async for m in reservationMapChannel.history(limit=200):
        if not checkedForOldMessage:
            checkedForOldMessage = True
            if m.created_at > message.created_at:
                return
        elif m.content in gamemodes.keys():
            gamemode = gamemodes[m.content]
        elif m.content == "!offline":
            return
    async with reservationMapChannel.typing():
        nations = await getReservedNations(reservationsChannel)
        print(gamemode)
        map = getColoredMap(nations, gamemode)
        map.save("reservations.png")
    
    async for m in reservationMapChannel.history(limit=200):
        if client.user == m.author:
            await m.delete()    
    m = await reservationMapChannel.send(content=createReservationsString(nations),file=discord.File("reservations.png"))
    
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    if message.guild == None:
       # if message.content == ('!help'):
        for i in range(0, len(helpResponse)):
            await message.channel.send(helpResponse[i])
        return
    gamemode = ""        
    print(message.channel.name)
    if message.channel.name.startswith("reservations_eu4"):
        gamemode = "eu4_VassalsInc"
    elif message.channel.name.startswith("reservations_vic2"):
        gamemode = "vic2_normal"
    elif message.channel.name.startswith("reservations_hoi4"):
        gamemode = "hoi4_normal"
    elif message.channel.name.startswith("reservations"):
        gamemode = "eu4_VassalsInc"
    else:
        return
    if gamemode != "" and message.content == "!deleteReservations" and (message.author.guild_permissions.administrator or message.author.id == 207462846336991232):
        async for m in message.channel.history(limit=200):
            await m.delete()    
        return
    if message.guild in activeOnGuild.keys():
        print("Spamm detected!")
        return
    else:
        activeOnGuild[message.guild] = 0
    
    #pick channel where reservations are done
    channels = message.guild.text_channels
    reservationsChannel = message.channel
    reservationMapChannel = None
    for i in channels:
        if i.name == message.channel.name + "_map" or i.name == message.channel.name + "map":
            reservationMapChannel = i
    if reservationMapChannel == None:
        activeOnGuild.pop(message.guild, None)
        await message.author.send("Error: no channel named \"" + message.channel.name + "_map\" found!")
        return          
    if message.guild.id not in guildsToTime.keys():
        guildsToTime[message.guild.id] = 0.0
    #reservationsChannel = message.channel
    nation = message.content.lower() if " " not in message.content else message.content.split(" ")[0].lower()   #ignore everything after whitespace
    nation = nation if "(" not in nation else nation.split("(")[0]   
    if message.content.startswith('!reservations') or nation in nationsToTag or nation in tagToPixel or message.content.startswith('!reserve '):
        if message.content.startswith('!reservations') or (time.time() - guildsToTime[message.guild.id] > 0):
            try:
                await updateMap(message, reservationsChannel, reservationMapChannel, gamemode)
            except Exception as e:
                await message.author.send("Error: \n" + str(e))
            guildsToTime[message.guild.id] = time.time()
         
           
    elif message.content == '!invalidMessages':
        messages = await getInvalidMessages(message.channel)
        msg = ""
        for m in messages.keys():
            msg += m.author.name +  ": " + m.content[0: 100] + "\n"
        if msg == "":
            msg = "No invalid Messages found"
        if len(msg) > 2000:
            msg = "To many invalid messages!"
        await message.channel.send(msg) 
    activeOnGuild.pop(message.guild, None)    
    
    
    
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    global oldtime

client.run(TOKEN)