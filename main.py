import discord
from discord import app_commands
from discord.ext import commands
from typing import Literal, Optional
from discord.ext.commands import Greedy, Context

import os
from dotenv import load_dotenv
import asyncio
import tracemalloc
import datetime
from discord import Activity, ActivityType
from functions.custom_functions import logging_setup

main_log = logging_setup(f"logs/{__name__}.log",f"pricing.{__name__}")

# Load environment variables from .env file
load_dotenv()
# Get bot token from environment variable
TOKEN = os.getenv("CHAINSMITH")

# Define intents
intents = discord.Intents.all()
intents.members = True

# Create bot instance
bot = commands.Bot(command_prefix=">", intents=intents)


# Load cogs on startup
@bot.event
async def on_ready():
    main_log.info(f"Bot {bot.application_id} has logged in .")
    await bot.change_presence(
        activity=Activity(type=ActivityType.watching, name="PRICE ACTION")
    )
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                main_log.info(f"{filename[:-3]} loaded successfully.")
            except Exception as e:
                main_log.error(f"Error loading {filename}: {e}")

@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
  ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        main_log.info(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
        return


@bot.event
async def on_message(message):
    if (
        isinstance(message.channel, discord.DMChannel)
        and message.content.lower() == "hi"
    ):
        welcome_message = """
    Hello there lovely!.\n You can type `register` to begin registering your coin on my data base"
    """
        await message.channel.send(welcome_message)

    await bot.process_commands(message)


## error handling for app commands
@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    if isinstance(error, app_commands.CommandOnCooldown):
        timeRemaining = str(datetime.timedelta(seconds=int(error.retry_after)))
        await interaction.response.send_message(
            f"wait for `{timeRemaining}` to use command again!", ephemeral=True
        )
        return
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            f"sorry You dont have the required permissions to use this command", ephemeral=True
        )
        return
    elif isinstance(error, app_commands.BotMissingPermissions):
        await interaction.response.send_message(
            f"sorry the bot doesn't have required permissions in this channel to perform that action", ephemeral=True
        )
        return
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            f"sorry you don't have required permissions in this channel to perform that action", ephemeral=True
        )
        return
    elif isinstance(error, app_commands.CommandInvokeError):
        await interaction.followup.send(
            f"invoke error", ephemeral=True
        )
        return
    else:
        await interaction.response.defer()
        await interaction.followup.send(
            "An error occurred while executing the command.", ephemeral=True
        )
        main_log.error(error)
        return
        


## error handling for commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.NotOwner):
        author = ctx.author
        try:
            await author.send(
                "FAFO :imp: \n You don't have permission to use that command."
            )
        except discord.errors.Forbidden:
            await ctx.reply("You're not the bot owner bruh")
        await ctx.message.delete()


tracemalloc.start()
timestamp = datetime.datetime.utcnow()


async def main():  
    await bot.start(TOKEN)

# Run the bot
asyncio.run(main())
