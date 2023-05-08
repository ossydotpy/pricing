import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
import tracemalloc,logging,logging.handlers
import datetime
from discord import Activity, ActivityType

# Load environment variables from .env file
load_dotenv()

# Get bot token from environment variable
TOKEN = os.getenv("TEST_BOT")

# Define intents
intents = discord.Intents.all()
intents.members = True

# Create bot instance
bot = commands.Bot(command_prefix=">", intents=intents)


# Load cogs on startup
@bot.event
async def on_ready():
    print("Bot is ready.")
    await bot.change_presence(
        activity=Activity(type=ActivityType.watching, name="PRICE ACTION")
    )
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"{filename[:-3]} loaded successfully.")
            except Exception as e:
                print(f"Error loading {filename}: {e}")


# Catch errors and throw helpful explanations
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send("Invalid command. Type !help for a list of available commands.")
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send("Missing required argument.")
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.send(
            f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds."
        )
    else:
        await ctx.send("An error occurred while executing the command.")

tracemalloc.start()
timestamp=datetime.datetime.utcnow()

async def main():  # Run the bot
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    await bot.start(TOKEN)


asyncio.run(main())
