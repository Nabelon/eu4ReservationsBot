import discord, json, os, time, sqlite3
from discord.ext import commands, tasks
from PIL import Image
import asyncio

with open('config.json') as config_file:
    config = json.load(config_file)

TOKEN = config['TOKEN']
tagToNations, tagToPixel, nationsToTag, nationColorsEU4 = {}, {}, {}, {}

with open(config['data_file']) as json_file:
    tagToNations = json.load(json_file)

with open(config['country_data_file']) as json_file:
    nationColorsEU4 = json.load(json_file)

for tag, data in tagToNations.items():
    for nation in data[0]:
        nationsToTag[nation.lower()] = tag
    nationsToTag[tag.lower()] = tag
    tagToPixel[tag] = [data[1], data[2]]

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents, help_command=None)

conn = sqlite3.connect('reservations.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS reservations (
    server_id INTEGER,
    channel_id INTEGER,
    user_id INTEGER,
    nation TEXT,
    date TEXT
)
''')
c.execute('''
CREATE TABLE IF NOT EXISTS reservation_logs (
    channel_id INTEGER PRIMARY KEY,
    gamemode TEXT,
    creation_date TEXT
)
''')
conn.commit()

async def getReservedNations(channel_id):
    nations = {}
    user_reservations = {}
    c.execute('SELECT * FROM reservations WHERE channel_id = ?', (channel_id,))
    rows = c.fetchall()
    for row in rows:
        user_id, nation = row[2], row[3]
        if user_id not in user_reservations:
            if nation in nationsToTag:
                user_reservations[user_id] = nationsToTag[nation]
                nations[nationsToTag[nation]] = [tagToPixel[nationsToTag[nation]], f'<@{user_id}>']
            elif nation in tagToNations:
                user_reservations[user_id] = nation
                nations[nation] = [tagToPixel[nation], f'<@{user_id}>']
    return nations

def getColoredMap(nations, gamemode):
    im = Image.open(os.path.join(config['image_dir'], gamemode + ".png"))
    pixels = im.load()
    colors = {(68, 107, 163): "water"}
    for nation, data in nations.items():
        if data[0] == [0, 0] and tagToNations[nation][0][0] in nationColorsEU4:
            cArray = nationColorsEU4[tagToNations[nation][0][0]]
            colors[(cArray[0], cArray[1], cArray[2])] = nation
        else:
            colors[pixels[data[0][0], data[0][1]]] = nation
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

async def updateMap(message, reservationsChannel, reservationMapChannel, gamemode):
    async with reservationMapChannel.typing():
        nations = await getReservedNations(reservationsChannel.id)
        map_img_path = "reservations.png"
        getColoredMap(nations, gamemode).save(map_img_path)
        embed = discord.Embed(title=f"Reservations ({len(nations)})", description="Reservations List", color=discord.Color.blue())
        embed.add_field(name="Reservations", value=createReservationsString(nations), inline=False)
        embed.set_image(url=f"attachment://reservations.png")
        file = discord.File(map_img_path, filename="reservations.png")
        async for m in reservationMapChannel.history(limit=200):
            if client.user == m.author: 
                await m.delete()
        await sendHelpMessage(reservationMapChannel) 
        await reservationMapChannel.send(embed=embed, file=file)

valid_gamemodes = config['gamemodes']

async def sendHelpMessage(channel):
    embed = discord.Embed(title="List of Commands", color=discord.Color.blue())
    embed.add_field(name="`!start [gamemode]`", value=f"Starts the reservation process for the specified gamemode. You must use this command before any reservations can be made.\nAvailable gamemodes: {', '.join(valid_gamemodes)}", inline=False)
    embed.add_field(name="`!reserve [nation]`", value="Reserves a nation for yourself. Make sure to start the reservation process with !start before using this command.", inline=False)
    embed.add_field(name="`!reserve [nation] [user]`", value="Allows game managers (those with mute permissions) to reserve a nation for another user.", inline=False)
    embed.add_field(name="`!unreserve`", value="Removes your current reservation. Game managers can also use this command to unreserve a nation for another user by mentioning them.", inline=False)
    embed.add_field(name="`!delete`", value="Deletes all reservations and the logged gamemode for the current channel. Only administrators can use this command.", inline=False)
    embed.add_field(name="`!help`", value="Displays this list of commands.", inline=False)
    embed.set_footer(text="Use these commands to manage your game's reservations.")
    await channel.send(embed=embed)

async def delete_after_delay(message, delay=5):
    await asyncio.sleep(delay)
    await message.delete()

@client.event
async def on_message(message):
    if message.author != client.user and message.guild:
        try:
            # Connect to the database
            conn = sqlite3.connect('reservations.db')
            c = conn.cursor()

            # Fetch the reservation log for the channel
            c.execute('SELECT * FROM reservation_logs WHERE channel_id = ?', (message.channel.id,))
            log = c.fetchone()

            if not log:
                if message.content.startswith("!start"):
                    parts = message.content.split()
                    gamemode = parts[1].lower() if len(parts) > 1 else config["default_gamemode"]

                    if gamemode not in valid_gamemodes:
                        await message.author.send(f"Error: Gamemode '{gamemode}' is not recognized. Please choose from the following: {', '.join(valid_gamemodes)}.")
                        await delete_after_delay(message)
                        return

                    try:
                        print(f"Starting reservations in channel {message.channel.name} for gamemode: {gamemode}")

                        c.execute('INSERT INTO reservation_logs (channel_id, gamemode, creation_date) VALUES (?, ?, ?)',
                                  (message.channel.id, gamemode, time.strftime('%Y-%m-%d %H:%M:%S')))
                        conn.commit()

                        await delete_after_delay(message)

                        await updateMap(message, message.channel, message.channel, gamemode=gamemode)

                        return
                    except Exception as e:
                        print(f"Error in !start command: {e}")
                        await message.author.send("An error occurred while starting the reservation. Please try again.")
                    return

                if message.content.startswith("!reserve") or message.content.startswith("!r "):
                    await message.author.send("Please use the !start command to initiate reservations before reserving a nation.")
                    await delete_after_delay(message)
                return

            if log:
                gamemode = log[1]

                if message.content.startswith("!reserve") or message.content.startswith("!r "):
                    try:
                        parts = message.content.split()
                        if len(parts) < 2:
                            await message.author.send("You must specify a nation to reserve.")
                            await delete_after_delay(message)
                            return

                        nation = parts[1].lower()
                        if len(message.mentions) > 0 and message.author.guild_permissions.mute_members:
                            user_id = message.mentions[0].id
                        else:
                            user_id = message.author.id

                        if nation in nationsToTag:
                            c.execute('SELECT nation FROM reservations WHERE channel_id = ? AND user_id = ?', (message.channel.id, user_id))
                            old_reservation = c.fetchone()
                            if old_reservation:
                                c.execute('DELETE FROM reservations WHERE channel_id = ? AND user_id = ?', (message.channel.id, user_id))
                                print(f"User <@{user_id}> switched from {old_reservation[0]} to {nation}.")
                            c.execute('INSERT INTO reservations (server_id, channel_id, user_id, nation, date) VALUES (?, ?, ?, ?, ?)',
                                      (message.guild.id, message.channel.id, user_id, nation, time.strftime('%Y-%m-%d %H:%M:%S')))
                            conn.commit()

                            await delete_after_delay(message)

                            await updateMap(message, message.channel, message.channel, gamemode=gamemode)
                        else:
                            await message.author.send(f"Nation '{nation}' not recognized.")
                            await delete_after_delay(message)
                    except Exception as e:
                        await message.author.send(f"Error: \n{str(e)}")
                        await delete_after_delay(message)
                        print(f"Error in !reserve command: {e}")
                    return

                if message.content.startswith("!unreserve"):
                    try:
                        user_id = message.author.id
                        if len(message.mentions) > 0:
                            if message.author.guild_permissions.mute_members:
                                user_id = message.mentions[0].id
                            else:
                                await message.author.send("You don't have permission to unreserve for others.")
                                await delete_after_delay(message)
                                return

                        c.execute('DELETE FROM reservations WHERE channel_id = ? AND user_id = ?', (message.channel.id, user_id))
                        conn.commit()

                        if log:
                            gamemode = log[1]
                            await updateMap(message, message.channel, message.channel, gamemode=gamemode)

                        await delete_after_delay(message)
                        print(f"User <@{user_id}> unreserved successfully in channel {message.channel.name}.")

                    except Exception as e:
                        await message.author.send(f"Error: \n{str(e)}")
                        await delete_after_delay(message)
                        print(f"Error in !unreserve command: {e}")
                    return

                if message.content.startswith("!delete"):
                    if message.author.guild_permissions.administrator:
                        try:
                            c.execute('DELETE FROM reservations WHERE channel_id = ?', (message.channel.id,))
                            c.execute('DELETE FROM reservation_logs WHERE channel_id = ?', (message.channel.id,))
                            conn.commit()

                            confirmation_message = await message.author.send("All reservations and logs have been deleted for this channel.")
                            
                            await delete_after_delay(message)
                            await delete_after_delay(confirmation_message, delay=10)

                            print(f"All reservations and logs deleted for channel {message.channel.name}.")

                        except Exception as e:
                            await message.author.send(f"Error: \n{str(e)}")
                            await delete_after_delay(message)
                            print(f"Error in !delete command: {e}")
                    else:
                        await message.author.send("You do not have permission to use this command.")
                        await delete_after_delay(message)
                    return

            # Ensure all other messages (commands) are deleted after processing
            await client.process_commands(message)
            await delete_after_delay(message)

        except sqlite3.Error as db_error:
            print(f"Database error: {db_error}")
            await message.author.send("An error occurred while accessing the database. Please contact the administrator.")
        except Exception as e:
            print(f"Unexpected error: {e}")
            await message.author.send("An unexpected error occurred. Please try again.")
        finally:
            # Ensure the database connection is closed after processing
            conn.close()

async def delete_messages_after_start(channel):
    async for message in channel.history(limit=200):
        if message.author != client.user:
            await message.delete()

async def delete_after_delay(message, delay=5):
    await asyncio.sleep(delay)
    await message.delete()


@client.command()
async def help(ctx):
    await sendHelpMessage(ctx.channel)

@tasks.loop(hours=12)
async def cleanup_old_reservations():
    cutoff = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() - 30 * 24 * 3600))
    c.execute('DELETE FROM reservations WHERE date < ?', (cutoff,))
    c.execute('DELETE FROM reservation_logs WHERE creation_date < ?', (cutoff,))
    conn.commit()

@client.event
async def on_ready():
    cleanup_old_reservations.start()
    print(f'Logged in as {client.user.name} ({client.user.id})\n------')

client.run(TOKEN)