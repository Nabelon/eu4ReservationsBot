# Discord Reservation Bot

This Discord bot is designed to manage nation reservations in a multiplayer gaming environment. It supports multiple servers and channels, allowing players to reserve nations, view current reservations, and manage the reservation process. The bot uses SQLite for data storage and can generate a map image highlighting the reserved nations.

---

## Features

- **Multi-Server and Multi-Channel Support**: The bot can operate in multiple servers and channels, maintaining separate reservation lists for each channel.
- **Nation Reservation**: Users can reserve a nation for themselves, and server managers can reserve nations for others.
- **Reservation Logging**: The bot logs all reservations and allows for the deletion and resetting of reservations.
- **Map Generation**: The bot generates an image highlighting the reserved nations, which is then posted in the channel.
- **Automated Cleanup**: Old reservations are automatically cleaned up every 12 hours.

---

## Commands

- **`!start [gamemode]`**: 
  - Initializes the reservation process for a specific game mode.
  - Example: `!start eu4`
  - **Note**: This command must be used before any reservations can be made.

- **`!reserve [nation]`**: 
  - Reserves a nation for yourself.
  - Example: `!reserve france`
  - **Note**: Ensure the reservation process has been started with `!start` before using this command.

- **`!reserve [nation] [user]`**: 
  - Allows game managers (those with mute permissions) to reserve a nation for another user.
  - Example: `!reserve france @username`

- **`!unreserve`**: 
  - Removes your current reservation.
  - Example: `!unreserve`
  - Game managers can also unreserve a nation for another user by mentioning them.
  - Example: `!unreserve @username`

- **`!delete`**: 
  - Deletes all reservations and the logged game mode for the current channel.
  - Example: `!delete`
  - **Note**: Only administrators can use this command.

- **`!help`**: 
  - Displays a list of available commands.
  - Example: `!help`

---

## How It Works

1. **Initialization**:
   - The bot is initialized with the configuration and data files (`config.json`, `data_file`, `country_data_file`) which contain necessary game and nation information.
   - The SQLite database is set up with tables for reservations and reservation logs.

2. **Starting a Reservation Session**:
   - A reservation session is started using the `!start [gamemode]` command.
   - The bot logs the game mode and channel ID in the database, ensuring that all subsequent reservations are associated with the correct game mode and channel.

3. **Reserving Nations**:
   - Users reserve nations by issuing the `!reserve [nation]` command.
   - The bot checks if the nation is valid and then logs the reservation in the database.
   - If the user already has a reservation, the bot will automatically switch the user's reservation to the new nation.
   
4. **Updating the Map**:
   - After each reservation, the bot generates an updated map image highlighting the reserved nations.
   - The image is posted in the channel along with a list of current reservations.

5. **Unreserving**:
   - Users can remove their reservations using the `!unreserve` command.
   - Game managers can remove reservations for other users by mentioning them.

6. **Deleting Reservations**:
   - Administrators can reset the reservation process in a channel using the `!delete` command.
   - This command deletes all reservations and logs for the channel, effectively starting fresh.

7. **Automated Cleanup**:
   - The bot periodically cleans up old reservations and logs that are older than 30 days.

---

### Project Updates:
This bot is an upgraded version of the original project by Ben. Improvements include:
- **Start command adds simplicity to the bot**.
- **Each person can only reserve one nation**.
- **Complete code overhaul, only similar thing is map generation**.
- **Compatability with latest version of discord.py**.
- **Added database for speed and ease of use**.

---

## Example Usage

1. **Start a Reservation Session**:

!start eu4

2. **Reserve a Nation**:

!reserve france

3. **Unreserve a Nation**:

!unreserve

4. **Delete All Reservations**:

!delete
