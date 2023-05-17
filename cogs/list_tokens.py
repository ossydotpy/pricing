import discord
from discord import app_commands
from discord.ext import commands
from buttons import Buttons

import json

class TokenList(commands.Cog):
    def __init__(self,bot:commands.Bot) -> None:
        self.bot = bot

    @staticmethod
    async def get_token_list():
        async with open("verified_tokens.json") as f:
            data = await json.load(f)
        return data
    
    @app_commands.command(name="token_list")
    @app_commands.checks.has_role("testorrrr🤓")
    async def token_list(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral= True)
        view= Buttons()
        view.add_item(
                    discord.ui.Button(
                        label="Submit Token Registraion",
                        emoji="<:logo:1107985387361685504>",
                        style=discord.ButtonStyle.link,
                        url="https://discordapp.com/users/638340154125189149",
                    )
                )
        try:
            data = self.get_token_list()
            token_list_embed = discord.Embed(title="📃 List of all registered tokens.")

            for token_detail in data:
                for token_name in token_detail.keys():
                    token_list_embed.add_field(name="",value=f"${token_name}")
            token_list_embed.set_thumbnail(url="https://i.ibb.co/m8srJ7S/logo.jpg")
            await interaction.followup.send(embed=token_list_embed,ephemeral=True,view=view)
            return
        except Exception as e:
            await interaction.followup.send("an error occured!, try again")
            print(e)
            return


async def setup(bot):
    await bot.add_cog(TokenList(bot))

    