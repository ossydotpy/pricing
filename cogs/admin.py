import discord
from discord import app_commands
from discord.ext import commands


class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="load")
    @commands.is_owner()
    async def load(self, interaction: discord.Interaction, extension: str):
        """load cogs"""
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.load_extension(f"cogs.{extension}")
            await interaction.followup.send(f"{extension} loaded!")
        except Exception as e:
            await interaction.followup.send(e)

    @app_commands.command(name="unload")
    @commands.is_owner()
    async def unload(self, interaction: discord.Interaction, extension: str):
        """unload cogs"""
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.unload_extension(f"cogs.{extension}")
            await interaction.followup.send(f"{extension} unloaded!")
        except Exception as e:
            await interaction.followup.send(e)

    @app_commands.command(name="reload")
    @commands.is_owner()
    async def reload(self, interaction: discord.Interaction, extension: str):
        """reload cogs"""
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.reload_extension(f"cogs.{extension}")
            await interaction.followup.send(f"{extension} reloaded!")
        except Exception as e:
            await interaction.followup.send(e)


async def setup(bot):
    await bot.add_cog(Admin(bot), guilds=[discord.Object(id=1096587951586164756)])
