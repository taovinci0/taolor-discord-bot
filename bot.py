import os
import discord
from discord import app_commands
from discord.ext import commands
import requests
import logging
import traceback
import sys
import json
import time
import dotenv
from prompt_transformer import transform_prompt
from image_handler import decode_base64_image, generate_random_seed

# Load environment variables
dotenv.load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Changed to DEBUG for more verbose logging
logger = logging.getLogger("taolor-bot")

# Get environment variables
CREATOR_API_KEY = os.getenv("CREATOR_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ALLOWED_CHANNEL_ID = int(os.getenv("ALLOWED_CHANNEL_ID", 0))
TAOLOGO_CHANNEL_ID = int(os.getenv("TAOLOGO_CHANNEL_ID", 0))
APPLICATION_ID = int(os.getenv("APPLICATION_ID", 0))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", 0))

# Rate limiting settings
# Track the last request time per user
last_request_time = {}
REQUEST_COOLDOWN = 30  # seconds between requests from the same user

# Set up the Discord bot with required intents
intents = discord.Intents.default()
# We don't need message_content privileged intent for slash commands
intents.message_content = False
intents.members = True  # Enable member tracking
bot = commands.Bot(command_prefix='!', intents=intents, application_id=APPLICATION_ID)

@bot.event
async def on_ready():
    # Set the bot's status to show as online with a custom status
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="over the Bittensor community"
        )
    )
    
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Application ID: {APPLICATION_ID}')
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
        for cmd in synced:
            logger.info(f"Command synced: {cmd.name}")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")
        logger.error(traceback.format_exc())

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle errors from slash commands and log them"""
    logger.error(f"Command error: {error}")
    logger.error(traceback.format_exc())
    await interaction.response.send_message(f"An error occurred: {error}", ephemeral=True)

@bot.event
async def on_member_join(member: discord.Member):
    """Handle new member joins"""
    try:
        # Get the welcome channel
        welcome_channel = bot.get_channel(WELCOME_CHANNEL_ID)
        if not welcome_channel:
            logger.error(f"Could not find welcome channel with ID {WELCOME_CHANNEL_ID}")
            return

        # Create a personalized welcome message
        welcome_message = (
            f"🌟 Welcome to our community, {member.mention}! 🌟\n\n"
            "I'm Michael Taolor, and I'm thrilled to have you join us. "
            "This space is dedicated to innovation, learning, and meaningful discussions about AI, blockchain, and technology.\n\n"
            "Feel free to:\n"
            "• Introduce yourself and share your interests\n"
            "• Ask questions and engage with our community\n"
            "• Explore our various channels and resources\n\n"
            "If you need any assistance, don't hesitate to ask. Let's create something amazing together! 🚀"
        )

        # Create a thread for the new member
        thread_name = f"Welcome {member.name}! 👋"
        thread = await welcome_channel.create_thread(
            name=thread_name,
            type=discord.ChannelType.public_thread,
            auto_archive_duration=1440  # Archive after 24 hours
        )

        # Generate and send the welcome image
        welcome_image = await generate_welcome_image(member.name)
        
        # Send the welcome message and image in the thread
        if welcome_image:
            await thread.send(welcome_message, file=welcome_image)
        else:
            await thread.send(welcome_message)

        logger.info(f"Sent welcome message to {member.name} in thread {thread.name}")
    except Exception as e:
        logger.error(f"Error in welcome message: {e}")
        logger.error(traceback.format_exc())

def check_rate_limit(user_id):
    """Check if a user is rate limited"""
    current_time = time.time()
    if user_id in last_request_time:
        time_diff = current_time - last_request_time[user_id]
        if time_diff < REQUEST_COOLDOWN:
            return False, REQUEST_COOLDOWN - time_diff
    
    # Update the last request time
    last_request_time[user_id] = current_time
    return True, 0

async def generate_image(interaction: discord.Interaction, scene_description: str, model_name: str, allowed_channel_id: int):
    """
    Common function to generate images using either model
    
    Args:
        interaction: The Discord interaction
        scene_description: User's scene description
        model_name: Which model to use (taolor-sfw or taolor-logo)
        allowed_channel_id: The channel ID where this command is allowed
    """
    # Check if the command is used in the allowed channel
    if interaction.channel_id != allowed_channel_id:
        logger.warning(f"Command used in wrong channel. Expected {allowed_channel_id}, got {interaction.channel_id}")
        await interaction.response.send_message(f"Please use this command in the designated channel. <#{allowed_channel_id}>", ephemeral=True)
        return
    
    # Check for rate limiting
    can_proceed, wait_time = check_rate_limit(interaction.user.id)
    if not can_proceed:
        logger.warning(f"User {interaction.user.id} is rate limited, must wait {wait_time:.1f} more seconds")
        await interaction.response.send_message(
            f"Please wait {wait_time:.1f} more seconds before generating another image.", 
            ephemeral=True
        )
        return
    
    # Let the user know we're processing their request
    logger.debug("Deferring response...")
    await interaction.response.defer(thinking=True)
    
    try:
        # Only transform prompt for taolor-sfw model
        if model_name == "taolor-sfw":
            prompt = transform_prompt(scene_description)
            logger.info(f"Original prompt: {scene_description}")
            logger.info(f"Transformed prompt: {prompt}")
        else:
            # For taolor-logo, use the original prompt
            prompt = scene_description
            logger.info(f"Using original prompt for logo: {prompt}")
        
        # Prepare API request
        url = "https://creator.bid/api/hub/text2image"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Discord-Bot/1.0",
            "x-api-key": CREATOR_API_KEY
        }
        data = {
            "prompt": prompt,
            "seed": generate_random_seed(),
            "loraName": model_name,
            "height": 1024,
            "width": 1024
        }
        
        # Send request to API
        logger.debug(f"Sending request to Creator.bid API using model: {model_name}...")
        logger.debug(f"Request data: {json.dumps(data)}")
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=60)
            logger.debug(f"API response status code: {response.status_code}")
            logger.debug(f"API response headers: {response.headers}")
            
            # Try to log the response text for debugging
            try:
                logger.debug(f"API response (first 500 chars): {response.text[:500]}")
            except Exception as e:
                logger.warning(f"Could not log response text: {e}")
            
        except requests.exceptions.Timeout:
            logger.error("API request timed out after 60 seconds")
            await interaction.followup.send("The image generation API is taking too long to respond. Please try again later.")
            return
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed with exception: {e}")
            await interaction.followup.send("Failed to connect to the image generation API. Please try again later.")
            return
        
        # Check if the request was successful
        if response.status_code == 200:
            try:
                resp_json = response.json()
                logger.debug("Successfully parsed API response JSON")
                if "image" in resp_json:
                    # Decode the base64 image
                    logger.debug("Decoding base64 image...")
                    image_bytes = decode_base64_image(resp_json["image"])
                    
                    # Create a file object for Discord
                    logger.debug("Creating Discord file...")
                    discord_file = discord.File(fp=image_bytes, filename="taolor.png")
                    
                    # Send the file with a message
                    logger.debug("Sending image to Discord...")
                    model_display_name = "Taolor" if model_name == "taolor-sfw" else "Bittensor Logo"
                    await interaction.followup.send(
                        f"**Your {model_display_name} image**: {scene_description}",
                        file=discord_file
                    )
                    logger.info("Successfully sent image to Discord")
                else:
                    logger.warning(f"API response did not contain an image. Response keys: {resp_json.keys()}")
                    if "error" in resp_json:
                        error_message = resp_json["error"]
                        logger.warning(f"API error message: {error_message}")
                        await interaction.followup.send(f"The API returned an error: {error_message}")
                    else:
                        await interaction.followup.send("The API didn't return an image. Please try again.")
            except Exception as e:
                logger.error(f"Error processing API response: {e}")
                logger.error(traceback.format_exc())
                await interaction.followup.send("An error occurred while processing the image. Please try again.")
        elif response.status_code == 429:
            # Rate limit reached
            logger.warning("API rate limit reached (429 status code)")
            await interaction.followup.send("The image generation API is currently rate limited. Please try again in a few minutes.")
        elif response.status_code == 402:
            # Payment required - possibly out of credits
            logger.error("API returned 402 Payment Required - possibly out of credits")
            await interaction.followup.send("The image generation service may be out of credits. Please contact the bot administrator.")
        else:
            logger.error(f"API request failed with status code: {response.status_code}")
            logger.error(f"API response: {response.text}")
            await interaction.followup.send("Failed to generate image. Please try again later.")
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        await interaction.followup.send("An unexpected error occurred. Please try again later.")

@bot.tree.command(name="create-image-taolor", description="Generate an image of Taolor based on your description")
@app_commands.describe(scene_description="Describe the scene you want to generate")
async def create_image_taolor(interaction: discord.Interaction, scene_description: str):
    # Debug info
    logger.debug(f"Received /create-image-taolor command from {interaction.user} in channel {interaction.channel_id}")
    logger.debug(f"Scene description: {scene_description}")
    
    await generate_image(interaction, scene_description, "taolor-sfw", ALLOWED_CHANNEL_ID)

@bot.tree.command(name="create-image-taologo", description="Generate an image with the Bittensor T Logo based on your description")
@app_commands.describe(scene_description="Describe any scene you want with the Bittensor T Logo")
async def create_image_taologo(interaction: discord.Interaction, scene_description: str):
    # Debug info
    logger.debug(f"Received /create-image-taologo command from {interaction.user} in channel {interaction.channel_id}")
    logger.debug(f"Scene description: {scene_description}")
    
    await generate_image(interaction, scene_description, "taolor-logo", TAOLOGO_CHANNEL_ID)

async def generate_welcome_image(member_name: str) -> discord.File:
    """Generate a welcome image for new members"""
    try:
        # Create a welcoming scene description
        scene_description = f"A warm and inviting scene of Michael Taolor standing in a modern, well-lit entrance hall with soft ambient lighting. He is wearing smart casual attire and has a genuine, welcoming smile. He is making a welcoming gesture with his hands, as if greeting someone. The timestamp shows the current moment. The scene should feel warm, professional, and welcoming."
        
        # Use the existing image generation logic
        url = "https://creator.bid/api/hub/text2image"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Discord-Bot/1.0",
            "x-api-key": CREATOR_API_KEY
        }
        data = {
            "prompt": scene_description,
            "seed": generate_random_seed(),
            "loraName": "taolor-sfw",
            "height": 1024,
            "width": 1024
        }
        
        logger.debug(f"Generating welcome image for {member_name}")
        response = requests.post(url, json=data, headers=headers, timeout=60)
        
        if response.status_code == 200:
            resp_json = response.json()
            if "image" in resp_json:
                image_bytes = decode_base64_image(resp_json["image"])
                return discord.File(fp=image_bytes, filename="welcome.png")
        
        logger.error(f"Failed to generate welcome image: {response.status_code}")
        return None
    except Exception as e:
        logger.error(f"Error generating welcome image: {e}")
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    # Check if required environment variables are set
    if not CREATOR_API_KEY:
        logger.error("CREATOR_API_KEY environment variable is not set!")
        exit(1)
    if not DISCORD_BOT_TOKEN:
        logger.error("DISCORD_BOT_TOKEN environment variable is not set!")
        exit(1)
    if ALLOWED_CHANNEL_ID == 0:
        logger.warning("ALLOWED_CHANNEL_ID is not set or invalid. Bot will not respond in any channel!")
    if TAOLOGO_CHANNEL_ID == 0:
        logger.warning("TAOLOGO_CHANNEL_ID is not set or invalid. /create-image-taologo will not work correctly!")
    
    # Print important configuration for debugging
    logger.info(f"Taolor SFW command configured for channel: {ALLOWED_CHANNEL_ID}")
    logger.info(f"Taolor Logo command configured for channel: {TAOLOGO_CHANNEL_ID}")
    logger.info(f"Application ID: {APPLICATION_ID}")
    
    # Start the bot
    logger.info("Starting the bot with commands: /create-image-taolor and /create-image-taologo")
    bot.run(DISCORD_BOT_TOKEN) 