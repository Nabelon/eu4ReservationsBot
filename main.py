# -*- coding: iso-8859-1 -*-
import discord, json, os, time
from discord.ext import commands
from PIL import Image

# Load config
with open('config.json') as config_file:
    config = json.load(config_file)

TOKEN, gamemodes, helpResponse, tagToNations, tagToPixel, nationsToTag, nationColorsEU4 = config['TOKEN'], config["gamemodes"], [''], {}, {}, {}, {}
with open(config['help_file'], "r") as myfile:
    helpResponse = [line for line in myfile.readlines() if len(helpResponse[-1]) + len(line) <= 1000] or helpResponse.append(line)
with open(config['data_file']) as json_file: tagToNations = json.load(json_file)
with open(config['country_data_file']) as json_file: nationColorsEU4 = json.load(json_file)
for tag, data in tagToNations.items():
    for nation in data[0]: nationsToTag[nation] = tag
    nationsToTag[tag], tagToPixel[tag] = tag, [data[1], data[2]]

intents, client = discord.Intents.all(), commands.Bot(command_prefix='!', intents=intents)

async def getReservedNations(channel):
    nations, user_reservations = {}, {}
    async for message in channel.history(limit=200, oldest_first=False):
        content, author_id = message.content.lower(), message.author.id
        if (content.startswith("!reserve ") or content.startswith("!r ")) and len(content.split()) > 1:
            nation = content.split()[1].split("(")[0]
            if author_id not in user_reservations:
                if nation in nationsToTag:
                    user_reservations[author_id] = nationsToTag[nation]
                    nations[nationsToTag[nation]] = [tagToPixel[nationsToTag[nation]], message.author.mention]
                elif nation in tagToNations:
                    user_reservations[author_id] = nation
                    nations[nation] = [tagToPixel[nation], message.author.mention]
    return nations

def getColoredMap(nations, gamemode):
    im = Image.open(os.path.join(config['image_dir'], gamemode + ".png"))
    pixels, colors = im.load(), {(68, 107, 163): "water"}
    for nation, data in nations.items():
        cArray = nationColorsEU4[tagToNations[nation][0][0]] if data[0] == [0, 0] and tagToNations[nation][0][0] in nationColorsEU4 else None
        colors[(cArray[0], cArray[1], cArray[2])] = nation if cArray else colors[pixels[data[0][0], data[0][1]]] = nation

    im = Image.open(os.path.join(config['image_dir'], gamemode + "_small.png"))
    pixels, width, height = im.load(), *im.size
    for i in range(width):
        for j in range(height):
            color = pixels[i, j]
            if (color != (68, 107, 163)) and ((i + 1 < width and pixels[i + 1, j] != color) or (j + 1 < height and pixels[i, j + 1] != color)):
                pixels[i, j] = (0, 0, 0)
            elif color not in colors:
                pixels[i, j] = (127, 127, 127)
    return im

def createReservationsString(nations):
    return "\n".join(sorted([f"{tagToNations[n][0][0].capitalize()} : {nations[n][1]}" for n in nations]))

async def updateMap(message, reservationsChannel, reservationMapChannel, gamemode=config["default_gamemode"]):
    async for m in reservationMapChannel.history(limit=200):
        if m.content.startswith("!gamemode="):
            gm = m.content.split("=")[1].lower()
            if gm in gamemodes: gamemode = gm
            else: raise ValueError('Unknown gamemode: ' + gm)
        elif m.content == "!offline": return
    async with reservationMapChannel.typing():
        nations = await getReservedNations(reservationsChannel)
        map_img_path = "reservations.png"
        getColoredMap(nations, gamemode).save(map_img_path)
        embed = discord.Embed(title=f"Reservations ({len(nations)})", description="Reservations List", color=discord.Color.blue())
        embed.add_field(name="Reservations", value=createReservationsString(nations), inline=False)
        embed.set_image(url=f"attachment://reservations.png")
        file = discord.File(map_img_path, filename="reservations.png")
        async for m in reservationMapChannel.history(limit=200):
            if client.user == m.author: await m.delete()
        await reservationMapChannel.send(embed=embed, file=file)

@client.event
async def on_message(message):
    if message.author != client.user and message.guild:
        if not message.channel.name.startswith("reservations") or message.channel.name.endswith("map"): return
        if message.content == "!deleteReservations" and (message.author.guild_permissions.administrator or message.author.id == 207462846336991232):
            async for m in message.channel.history(limit=200): await m.delete()
            return
        if message.guild in activeOnGuild: return print("Spam detected!")
        activeOnGuild[message.guild] = 0
        reservationsChannel, reservationMapChannel = message.channel, None
        for ch in message.guild.text_channels:
            if ch.name in [message.channel.name + "_map", message.channel.name + "map"]:
                reservationMapChannel = ch
                break
        if not reservationMapChannel:
            activeOnGuild.pop(message.guild, None)
            return await message.author.send(f"Error: no channel named \"{message.channel.name}_map\" found!")
        if any(message.content.startswith(cmd) for cmd in ['!reservations', '!reserve ', '!r ']) or any(nation in message.content.lower() for nation in nationsToTag):
            try: await updateMap(message, reservationsChannel, reservationMapChannel)
            except Exception as e: await message.author.send(f"Error: \n{str(e)}")
            guildsToTime[message.guild.id] = time.time()
        activeOnGuild.pop(message.guild, None)

@client.event
async def on_ready(): print(f'Logged in as {client.user.name} ({client.user.id})\n------')

client.run(TOKEN)
