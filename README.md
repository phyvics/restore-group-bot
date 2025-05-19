# Telegram Channel to Group Message Restorer Bot

A powerful Telegram bot that can replicate and restore messages from a channel to a group. This bot is particularly useful for:
- Creating backups of important channel content
- Migrating content from one channel to another
- Restoring deleted or lost messages
- Maintaining a synchronized copy of channel content in a group

## Features

- 🔄 **Automatic Forwarding**: New messages posted in the channel are automatically forwarded to the group
- 📥 **Full Restoration**: Restore all existing messages from the channel to the group with a single command
- 🔒 **Access Control**: Only authorized users can trigger the restoration process
- ⚡ **Real-time Updates**: Messages are forwarded instantly as they are posted
- 🛡️ **Error Handling**: Robust error handling and rate limiting to prevent API issues
- 🔍 **Chat Information**: Get IDs and details of configured channels and groups

## Prerequisites

- Python 3.7 or higher
- A Telegram Bot Token (get one from [@BotFather](https://t.me/BotFather))
- A source Telegram Channel (must be a supergroup/channel)
- A target Telegram Group (must be a supergroup)
- Bot must be an admin in both the channel and group with send messages permissions

## Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/phyvics/restore-group-bot.git
   cd restore-group-bot
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot:**
   1. Create a new bot:
      - Message [@BotFather](https://t.me/BotFather) on Telegram
      - Send `/newbot` and follow the instructions
      - Copy the bot token provided by BotFather
   
   2. Initial bot setup:
      - Open `config.py`
      - Replace `YOUR_BOT_TOKEN_HERE` with the token from BotFather
      - Save the file
   
   3. Add the bot to your channel and group:
      - Add the bot as an admin to your source channel with read messages permission
      - Add the bot as an admin to your target group with send messages permission
   
   4. Get the channel and group IDs:
      - Start the bot by running `python main.py`
      - Send `/start` to the bot
      - Send `/getids` to get the IDs of the channel and group
      - Note down the IDs shown in the response
      - Stop the bot (Ctrl+C)
   
   5. Final configuration:
      - Open `config.py` again
      - Replace the channel and group IDs with the ones you got from `/getids`
      - Add your Telegram user ID to `AUTHORIZED_USERS` to be able to use admin commands
      - Save the file
   
   6. Start the bot again:
      - Run `python main.py`
      - The bot is now fully configured and ready to use

5. **Set up bot permissions:**
   - Add the bot to your channel as an admin with permission to read messages
   - Add the bot to your group as an admin with permission to send messages
   - The bot only needs send message permissions in the group

## Running the Bot

1. **Start the bot:**
   ```bash
   python main.py
   ```

2. **Using the bot:**
   - Send `/start` to see the welcome message
   - Send `/help` to see available commands
   - Send `/restore` to start the message restoration process
   - Send `/getids` to view IDs and details of configured channels and groups
   - Send `/cancel` to cancel any ongoing operation

## Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help message with available commands
- `/restore` - Start the message restoration process
- `/getids` - View IDs and details of configured channels and groups (admin only)
- `/cancel` - Cancel any ongoing operation

## Important Notes

- The bot requires admin privileges in both the source channel and target group
- The restoration process may take some time depending on the number of messages
- Telegram has rate limits, so the bot includes delays between message forwards
- Keep your `config.py` file secure and never commit it to version control
- The bot will automatically forward new messages as they are posted in the channel
- Use `/getids` command to verify channel and group IDs without using external bots

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Support

If you encounter any issues or have questions, please open an issue in the GitHub repository. 