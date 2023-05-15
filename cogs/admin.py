import discord
from discord import app_commands
from discord.ext import commands

import os
from dotenv import load_dotenv

load_dotenv()
OWNER_ID = int(os.getenv("OWNER_ID"))
class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="load")
    async def load(self, interaction: discord.Interaction, extension: str):
        """reload cogs"""
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id == OWNER_ID:
            try:
                await self.bot.load_extension(f"cogs.{extension}")
                await interaction.followup.send(f"{extension} loaded!")
            except Exception as e:
                await interaction.followup.send(e)
        else:
            await interaction.followup.send("this command is reserved for bot creator only")

    @app_commands.command(name="unload")
    async def unload(self, interaction: discord.Interaction, extension: str):
        """reload cogs"""
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id == OWNER_ID:
            try:
                await self.bot.unload_extension(f"cogs.{extension}")
                await interaction.followup.send(f"{extension} unloaded!")
            except Exception as e:
                await interaction.followup.send(e)
        else:
            await interaction.followup.send("this command is reserved for bot creator only")

    @app_commands.command(name="reload")
    async def reload(self, interaction: discord.Interaction, extension: str):
        """reload cogs"""
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id == OWNER_ID:
            try:
                await self.bot.reload_extension(f"cogs.{extension}")
                await interaction.followup.send(f"{extension} reloaded!")
            except Exception as e:
                await interaction.followup.send(e)
        else:
            await interaction.followup.send("this command is reserved for bot creator only")


async def setup(bot):
    await bot.add_cog(Admin(bot))

# app_commands.check()
