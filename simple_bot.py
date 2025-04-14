import os
import discord
from discord import app_commands
from discord.ext import commands
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Get environment variables
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ALLOWED_CHANNEL_ID = int(os.getenv("ALLOWED_CHANNEL_ID", 0))
APPLICATION_ID = int(os.getenv("APPLICATION_ID", 0))

# Set up the Discord bot with default intents and application ID
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents, application_id=APPLICATION_ID)

@bot.event
async def on_ready():
    print(f"Bot is connected to Discord as {bot.user}")
    print(f"Bot is configured to respond in channel: {ALLOWED_CHANNEL_ID}")
    print(f"Application ID: {APPLICATION_ID}")
    
    # Sync commands
    try:
        print("Syncing commands...")
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="hello", description="Test if the bot is working")
async def hello(interaction: discord.Interaction):
    # Check if the command is used in the allowed channel
    if interaction.channel_id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message(f"Please use this command in the designated channel (ID: {ALLOWED_CHANNEL_ID}).", ephemeral=True)
        return
    
    await interaction.response.send_message("Hello! The bot is working correctly.")

if __name__ == "__main__":
    print("Starting the bot...")
    print(f"Using token: {DISCORD_BOT_TOKEN[:5]}...{DISCORD_BOT_TOKEN[-5:]}")
    bot.run(DISCORD_BOT_TOKEN) 