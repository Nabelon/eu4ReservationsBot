# eu4reservations
A discord bot for EU4 multiplayer games

Join https://discord.gg/Gd6TJXzYMg if you need help
Add this bot to your server: https://discord.com/oauth2/authorize?client_id=733588874500243486&scope=bot

How to use:
Create two channels on your server, one names reservations and one named reservationsmap
Make sure the bot has read rights in the reservations channel and read+write rights in the reservationsmap channel
If you want to use !deleteReservations it also needs edit rights in the reservations channel

The bot waits for a message in #reservations, if its a nation it posts an updated map in #reservationsmap, !reservations can be used to force the bot to update if you don't want to reserve anything but still update the map (e.g. after someone deleted/edited a message).
The bot ONLY updates the map when a new message is send in #reservations, if you change/delete past messages map will not update immediately and you need to send a new reservation or !reservations in the #reservations channel

#Nations with spaces in their name DO NOT WORK by default, either use their tag or "_" instead of space

Because i have to add each nation manually to a list, not all will be present on the map and some won't even be registered as a country. Whisper me if you want me to add any nation or help out.

The bot is single threaded and may not respond immediately if another server uses it at the same time.

Write \"!1444\" in #reservationsmap if you don't want vassals to be merged with their overlord (makes france and muscovy look ugly)
Write \"!reserve fra Max\" in #reservation to reserve France for the player called Max
Write !offline  in #reservationsmap if you want the bot to not do anything right now.

Bot is hosted for free atm and the host only allows for 450 hours hosting time per month, if bot if offline at end of month said limit has been reached :(

For HOI4 and VIC2, create a reservations_hoi4/reservations_vic2 channel for reservations and a reservations_hoi4_map/reservations_vic2_map channel for the map"