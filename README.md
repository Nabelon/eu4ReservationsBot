<div align="center">
    <img src="https://i.imgur.com/F60J2JS.png" alt="Discord Relay Bot" width="100" />
    <h1>EU4ReservationsBot</h1>
</div>

## **Table of Contents**
- [Introduction](#introduction)
- [Features](#features)
- [How to Use](#how-to-use)
- [Commands](#commands)
- [Installation](#installation)
-- [Configuration](##configuration)
-- [Running the Bot](##running-the-bot)
-- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

---

## **Introduction**

Welcome to **EU4ReservationsBot**—your go-to solution for efficiently managing nation reservations within Discord servers. Whether you're hosting an EU4 multiplayer session or a Hearts of Iron 4 campaign, this bot is designed to simplify the reservation process and enhance the overall experience for your community.

[**Invite the Bot to Your Server**](https://discord.com/oauth2/authorize?client_id=733588874500243486&scope=bot)  
*Click the link above to add the bot to your Discord server!*

---

## **Features**

- **Nation Reservations:** Effortlessly reserve nations across multiple supported game modes, ensuring a fair and organized process where no two users can reserve the same nation.
- **Dynamic Map Generation:** The bot automatically generates a visual map reflecting the current reservations, providing a clear and engaging way to view reservations.
- **Automated Cleanup:** To maintain an orderly server, the bot automatically removes expired reservations after 30 days, ensuring your channel remains clutter-free.
- **DM Notifications:** Enjoy personalized notifications delivered directly to your DMs, including error messages, reservation confirmations, and more.
- **Admin Privileges:** A comprehensive suite of admin commands allows you to manage reservations, view logs, and maintain the database with ease.

---

## **how-to-use**

Step 1) [**Invite the Bot to Your Server**](https://discord.com/oauth2/authorize?client_id=733588874500243486&scope=bot) 
Step 2)	Write "!start" in the channel you want use for the resevations
Step 3) You are done, reserve nations by writing "!reserve [Nation]"

---

## **Commands**

Below is a list of commands available in the EU4ReservationsBot:

- `!start [gamemode]`: Initiates the reservation process for the specified game mode. Must be executed before any reservations can be made.
- `!reserve [nation]`: Reserves a nation for yourself. This command can be used after the reservation process is initiated.
- `!reserve [nation] [user]`: Allows game managers to reserve a nation on behalf of another user.
- `!unreserve`: Cancels your current reservation. Game managers can also unreserve a nation for another user by mentioning them.
- `!delete`: Deletes all reservations and the logged game mode for the current channel. Only administrators are permitted to use this command.
- `!help`: Displays a comprehensive list of available commands and their descriptions.

---

## **Installation**

If you want to host EU4ReservationsBot on your local machine or modify it, follow these steps.

1. **Clone the Repository**

   Begin by cloning the repository to your local environment:

   ```git clone https://github.com/your-username/discord-reservation-bot.git```

2. **Install Dependencies**

   Ensure Python 3.7+ is installed, then proceed to install the required Python libraries:

   ```pip install -r requirements.txt```

3. **Create and Configure `config.json`**

   Add a `token.txt` file in the root directory containing the token of your Discord bot.

4. **Set Up the Database**

   The bot utilizes SQLite for managing reservations. The required tables will be automatically created when the bot is first run.

---

## **Configuration**

### **Data Files**

- `data/tags.json`: Maps country tags to nation names and pixel locations on the map for accurate visual representation.
- `data/country_colors.json`: Specifies nation colors for the `eu4` game mode, ensuring accurate map visuals.
- **Images:** Store your game mode-specific map images in the `images/` directory. The bot loads these images to generate the reservation map.

---

## **Running the Bot**

After setup, you can launch the bot using the following command:

```python main.py```

Once launched, the bot will connect to your Discord server and start listening for commands, ready to manage reservations.

---

## **Contributing**

We welcome and appreciate contributions to enhance EU4ReservationsBot. Here’s how you can contribute:

1. **Fork the Repository:** Use the "Fork" button at the top-right of the repository page.
2. **Clone Your Fork:** Clone the forked repository to your local machine.
3. **Create a New Branch:** Start a new branch for your specific feature or bugfix.
4. **Make Your Changes:** Implement your changes or bug fixes.
5. **Commit Your Changes:** Write a clear, descriptive commit message summarizing your changes.
6. **Push to Your Branch:** Push your changes to your forked repository.
7. **Submit a Pull Request:** Open a pull request on the original repository for review.

---

## **Support**

For assistance, feel free to join our [Discord server](https://discord.gg/zcu5aFwKGf) or open an issue on GitHub. We encourage contributions, feedback, and suggestions to continuously improve the bot.

---

## **License**

This project is licensed under the MIT License. Please refer to the LICENSE file for more details.

---
