Project: Taolor Image Generator Discord Bot

🔍 Overview

This bot allows users in a specific Discord channel to generate AI images of "Taolor" (a man with grey hair and beard) using the Creator.bid image generation API. Each image will include a Bittensor "T Logo" placed somewhere specific within the scene.

📊 Objectives

Enable users to generate images using a /create slash command.

Automatically enforce brand identity (Taolor + T Logo).

Restrict image generation to a specific Discord channel.

Handle prompt formatting and image decoding internally.

⚖️ Technical Stack

Language: Python

Discord SDK: discord.py with discord.commands or nextcord

Image API: https://creator.bid/api/hub/text2image

Editor: Cursor

🔐 API Info

Endpoint: POST https://creator.bid/api/hub/text2image

Model: TaolorAndLogo

Key: (stored securely, e.g. .env file)

Response: base64-encoded image string

⚙️ Command: /create

Usage:

/create <scene description>

User Input Example:

/create in a dark dojo preparing to fight

Transformed Prompt:

A man with grey hair and beard is in a dark dojo preparing to fight, with a T Logo glowing on the wall behind him.

🔄 Prompt Transformation Rules

Always start with: "A man with grey hair and beard"

Always include a "T Logo" and describe where it is (e.g., "on chest", "on wall")

Do not force phrases like "blue neon color atmosphere scene"

If user mentions "full body", add a footwear line (e.g., "He is wearing black boots.")

🚫 Channel Restriction

Bot should only respond in a specific channel, identified by its ID.

In other channels, it returns: "Please use this command in the designated channel."

📤 Image Handling

Randomize seed per request

Decode base64 response into an image file

Send image as a file upload in Discord

📦 What to Include in the Project

.env file: Store your Creator.bid API key like:

CREATOR_API_KEY=your_key_here

Python Dependencies: Add to requirements.txt or install manually:

discord.py
python-dotenv
requests

Files to Create:

bot.py – the Discord bot logic

prompt_transformer.py – handles formatting user input

image_handler.py – (optional) handles decoding base64 to image

📆 Implementation Plan

Build prompt transformer logic (Python function)

Create basic Discord bot structure with discord.py

Add /create command handler

Add channel restriction logic

Connect to Creator.bid API with seed randomizer

Decode image and send it to Discord

Test everything in Cursor before deployment

🔎 Notes

Everything centers around Taolor and the T Logo — no other subjects allowed.

Users never have to mention "Taolor" or "T Logo" — the bot handles enforcement.

Future iterations could allow toggles (e.g., theme presets, random scenes).

End of Scope Document ✅ 