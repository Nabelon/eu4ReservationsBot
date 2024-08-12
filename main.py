# -*- coding: iso-8859-1 -*-
import discord
import json
from PIL import Image
from discord.ext import commands
import os
import time
import sys

# Load config
with open('config.json') as config_file:
    config = json.load(config_file)

TOKEN = config['TOKEN']
helpResponse = ['']
with open(config['help_file'], "r") as myfile:
    helpResponseTmp = myfile.readlines()
    indexCurr = 0
    for line in helpResponseTmp:
        if len(helpResponse[indexCurr]) + len(line) > 1000:
            helpResponse.append(line)
            indexCurr += 1
        else:
            helpResponse[indexCurr] += line

# Define intents
intents = discord.Intents.all()

client = commands.Bot(command_prefix='!', intents=intents)
nationsToTag, tagToNations, tagToPixel = {}, {}, {}
guildsToTime, activeOnGuild = {}, {}
gamemodes = config["gamemodes"]

with open(config['data_file']) as json_file:
    tagToNations = json.load(json_file)

with open(config['country_data_file']) as json_file:
    nationColorsEU4 = json.load(json_file)

for tag, data in tagToNations.items():
    for nation in data[0]:
        nationsToTag[nation] = tag
    nationsToTag[tag] = tag
    tagToPixel[tag] = [data[1], data[2]]

async def getReservedNations(channel):
    nations = {}
    user_reservations = {}  # Dictionary to store the most recent reservation per user

    # Process the message history in reverse to prioritize the most recent messages
    async for message in channel.history(limit=200, oldest_first=False):
        content = message.content.lower()
        if content.startswith("!reserve ") or content.startswith("!r "):
            parts = content.split()
            if len(parts) > 1:
                nation = parts[1].split("(")[0]  # This assumes the nation is the second word in the message
                author_id = message.author.id  # Use author ID to track reservations
                authorMention = message.author.mention
                
                # Only assign the latest reservation by checking if the user has already reserved a nation
                if author_id not in user_reservations:
                    if nation in nationsToTag:
                        user_reservations[author_id] = nationsToTag[nation]
                        nations[nationsToTag[nation]] = [tagToPixel[nationsToTag[nation]], authorMention]
                    elif nation in tagToNations:
                        user_reservations[author_id] = nation
                        nations[nation] = [tagToPixel[nation], authorMention]

    return nations

def getColoredMap(nations, gamemode):
    im = Image.open(os.path.join(config['image_dir'], gamemode + ".png"))
    pixels = im.load()
    colors = {(68, 107, 163): "water"}
    for nation, data in nations.items():
        if data[0][0] == 0 and data[0][1] == 0 and tagToNations[nation][0][0] in nationColorsEU4:
            cArray = nationColorsEU4[tagToNations[nation][0][0]]
            colors[(cArray[0], cArray[1], cArray[2])] = nation
        else:
            colors[pixels[data[0][0], data[0][1]]] = nation

    im = Image.open(os.path.join(config['image_dir'], gamemode + "_small.png"))
    pixels = im.load()
    width, height = im.size
    for i in range(width):
        for j in range(height):
            color = pixels[i, j]
            if (color != (68, 107, 163)) and ((i + 1 < width and pixels[i + 1, j] != color) or (j + 1 < height and pixels[i, j + 1] != color)):
                pixels[i, j] = (0, 0, 0)
            elif color not in colors:
                pixels[i, j] = (127, 127, 127)
    return im

def createReservationsString(nations):
    reservationsStr = ""
    nationsArr = [f"{tagToNations[n][0][0].capitalize()} : {nations[n][1]}" for n in nations]
    reservationsStr += "\n".join(sorted(nationsArr))
    return reservationsStr

async def updateMap(message, reservationsChannel, reservationMapChannel, gamemode=config["default_gamemode"]):
    async for m in reservationMapChannel.history(limit=200):
        if m.content.startswith("!gamemode=") and len(m.content) > 11:
            gm = m.content.split("=")[1].lower()
            if gm in gamemodes:
                gamemode = gm
            else:
                raise ValueError('Unknown gamemode: ' + gm)
        elif m.content == "!offline":
            return
    async with reservationMapChannel.typing():
        nations = await getReservedNations(reservationsChannel)
        map_img = getColoredMap(nations, gamemode)
        map_img_path = "reservations.png"
        map_img.save(map_img_path)

    # Create embed for the reservation message
    embed = discord.Embed(
        title=f"Reservations ({len(nations)})",
        description="Reservations List",
        color=discord.Color.blue()  # You can choose any color you prefer
    )

    embed.add_field(name="Reservations", value=createReservationsString(nations), inline=False)

    # Attach the image within the embed
    file = discord.File(map_img_path, filename="reservations.png")
    embed.set_image(url=f"attachment://reservations.png")

    async for m in reservationMapChannel.history(limit=200):
        if client.user == m.author:
            await m.delete()

    await reservationMapChannel.send(embed=embed, file=file)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Handle direct messages
    if message.guild is None:
        for response in helpResponse:
            await message.channel.send(response)
        return

    # Handle only reservation-related channels
    if not message.channel.name.startswith("reservations") or message.channel.name.endswith("map"):
        return

    # Delete reservations if admin command
    if message.content == "!deleteReservations" and (message.author.guild_permissions.administrator or message.author.id == 207462846336991232):
        async for m in message.channel.history(limit=200):
            await m.delete()
        return

    # Prevent spam detection
    if message.guild in activeOnGuild:
        print("Spam detected!")
        return

    activeOnGuild[message.guild] = 0

    # Find the associated map channel
    channels = message.guild.text_channels
    reservationsChannel, reservationMapChannel = message.channel, None
    for ch in channels:
        if ch.name == message.channel.name + "_map" or ch.name == message.channel.name + "map":
            reservationMapChannel = ch
            break

    if not reservationMapChannel:
        activeOnGuild.pop(message.guild, None)
        await message.author.send(f"Error: no channel named \"{message.channel.name}_map\" found!")
        return

    # Update map for !reservations or any reservation command
    if message.content.startswith('!reservations') or message.content.startswith('!reserve ') or message.content.startswith('!r ') or any(nation in message.content.lower() for nation in nationsToTag):
        try:
            await updateMap(message, reservationsChannel, reservationMapChannel)
        except Exception as e:
            await message.author.send(f"Error: \n{str(e)}")
        guildsToTime[message.guild.id] = time.time()

    activeOnGuild.pop(message.guild, None)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name} ({client.user.id})')
    print('------')

client.run(TOKEN)
