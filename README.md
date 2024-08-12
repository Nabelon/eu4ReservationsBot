# EU4Reservations Bot

A Discord bot for managing EU4 multiplayer game reservations.

### Quick Links:
- **[Join the Support Server](https://discord.gg/zcu5aFwKGf)**
- **[Add the Bot to Your Server](https://discord.com/oauth2/authorize?client_id=733588874500243486&scope=bot)**

### Setup:
1. **Create Channels:**
   - `#reservations`: The channel where players will reserve their nations.
   - `#reservationsmap`: The channel where the bot will post the updated map.

2. **Bot Permissions:**
   - `#reservations`: Ensure the bot has read permissions.
   - `#reservationsmap`: Ensure the bot has read and write permissions.
   - If you want to use `!deleteReservations`, the bot needs edit permissions in the `#reservations` channel.

### How to Use:
- The bot listens for messages in the `#reservations` channel. If a valid nation is reserved, it updates the map in the `#reservationsmap` channel.
- To force an update without reserving a nation (e.g., after deleting/editing a message), use the `!reservations` command in `#reservations`.
- **Important:** The bot updates the map only when a new message is sent in `#reservations`. If you change or delete past messages, the map won't update until a new reservation is made or `!reservations` is used.

### Nation Name Format:
- **Nations with spaces** in their names do not work by default. Use their tag or replace spaces with underscores (`_`).

### Commands:
- `!1444` in `#reservationsmap`: Prevents vassals from being merged with their overlord (e.g., France and Muscovy).
- `!reserve fra Max` in `#reservations`: Reserves France for the player named Max.
- `!offline` in `#reservationsmap`: Temporarily disables the bot.
- `!geckoV4` in `#reservationsmap`: Use if playing with the geckoV4 mod.
- `!AnteBellum` in `#reservationsmap`: Use if playing with the AnteBellum mod.

### Additional Information:
- For HOI4 and VIC2, create `#reservations_hoi4 / #reservations_vic2` channels for reservations and `#reservations_hoi4_map / #reservations_vic2_map` channels for the map.

---

### Project Updates:
This bot is an upgraded version of the original project by Ben. Improvements include:
- **One country per person** restriction.
- **Enhanced reservation message design**.
- **Code improvements**.
- **Compatibility with the latest version of discord.py**.
