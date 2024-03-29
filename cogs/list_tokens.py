import discord
from discord import app_commands
from discord.ext import commands
from functions.buttons import Buttons

import json
from functions.custom_functions import logging_setup

token_list_log = logging_setup(f"logs/{__name__}.log",f"pricing.{__name__}")

class TokenList(commands.Cog):
    def __init__(self,bot:commands.Bot) -> None:
        self.bot = bot

    @staticmethod
    def get_token_list():
        with open("verified_tokens.json") as f:
            data = json.load(f)
        return data
    
    @app_commands.command(name="token_list")
    async def token_list(self, interaction: discord.Interaction):
        """
        Show a list of verified tokens
        """
        await interaction.response.defer(ephemeral= True)
        token_data = self.get_token_list()
        if token_data:
            token_list_embed = discord.Embed(title="📃 List of all registered tokens.")

            for token_detail in token_data:
                for token_name in token_detail.keys():
                    token_list_embed.add_field(name="",value=f"${token_name}")
                    
            token_list_embed.set_thumbnail(url="https://i.ibb.co/rvTpW2X/logo.png")
            view= Buttons()
            view.add_item(
                discord.ui.Button(
                    label="Submit Token Registraion",
                    emoji="<:transparentlogo:1114079453258203187>",
                    style=discord.ButtonStyle.link,
                    url="https://discord.gg/2sUZ3YShm6",
                )
            )
            await interaction.followup.send(embed=token_list_embed,ephemeral=True,view=view)
            
        else:
            await interaction.followup.send(content="No registered token found")
        



async def setup(bot):
    await bot.add_cog(TokenList(bot))

    