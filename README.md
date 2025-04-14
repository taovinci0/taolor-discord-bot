# Taolor Discord Bot

A Discord bot that generates AI images using the Creator.bid API. The bot supports two different image generation commands:

## Features

- `/create-image-taolor` - Generates images of Taolor in various scenes with automatic prompt enhancement
- `/create-image-taologo` - Generates images incorporating the Bittensor T Logo based on user descriptions

## Setup

1. Clone the repository:
```bash
git clone https://github.com/taovinci0/taolor-discord-bot.git
cd taolor-discord-bot
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:
```
CREATOR_API_KEY=your_creator_bid_api_key
DISCORD_BOT_TOKEN=your_discord_bot_token
ALLOWED_CHANNEL_ID=channel_id_for_taolor_command
TAOLOGO_CHANNEL_ID=channel_id_for_logo_command
APPLICATION_ID=your_discord_application_id
```

4. Run the bot:
```bash
python bot.py
```

## Commands

- `/create-image-taolor` - Available in the designated Taolor channel
  - Generates an image of Taolor based on your description
  - Includes automatic prompt enhancement for better results

- `/create-image-taologo` - Available in the designated Logo channel
  - Generates an image incorporating the Bittensor T Logo
  - Uses raw prompts without transformation

## Rate Limiting

- Users are rate-limited to one request every 30 seconds
- Each command is restricted to its designated channel

## Error Handling

The bot includes comprehensive error handling for:
- API rate limits
- Invalid channels
- Failed image generation
- API timeouts
- Credit/payment issues

## Contributing

Feel free to submit issues and pull requests to improve the bot. 