import discord
from discord import app_commands
from discord.ext import commands

import os
import json
import requests
import asyncio

from buttons import Buttons

import minswap.assets as minas


class Total(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token_dict = {}

        with open("verified_tokens.json") as tokens:
            data = json.load(tokens)
            for info in data:
                for ticker, info in info.items():
                    self.token_dict[ticker] = info

    def get_token_info(self, ticker):
        if ticker in self.token_dict:
            return self.token_dict[ticker]
        else:
            return None

    @app_commands.command(name="how_many")
    async def how_many(
        self, interaction: discord.Interaction, ticker: str, stake_addr: str
    ):
        """check the price of your tokens"""
        await interaction.response.defer()
        token_info = self.get_token_info(ticker.upper())
        if not token_info:
            await interaction.followup.send(
                f"Invalid ticker: ${ticker.upper()}", ephemeral=True
            )
            return
        asset = str(
            token_info["policy_id"] + token_info["token_hex"]
        )  # name of assets as stored on the chain

        # get assets in the stake address
        url = f"https://cardano-mainnet.blockfrost.io/api/v0/accounts/{stake_addr}/addresses/assets"
        header = {"PROJECT_ID": os.getenv("PROJECT_ID")}
        response = requests.get(url=url, headers=header)
        data = response.json()
        # for i, asset in enumerate(data):
        #     unit = asset["unit"]
        for item in data:
            unit = item["unit"]
            amount = item["quantity"]
            if asset in str(unit):
                total_embed = discord.Embed(
                    title=f"how many ${ticker.upper()} do you hold?"
                )
                total_embed.add_field(name="Token", value=f"${ticker.lower()}")
                total_embed.add_field(name="Amount Held", value=f"{amount}")
                view = Buttons()
                view.add_item(
                    discord.ui.Button(
                        label="Report",
                        style=discord.ButtonStyle.link,
                        url="https://discordapp.com/users/638340154125189149",
                    )
                )

                try:
                    await asyncio.sleep(3)
                    await interaction.followup.send(
                        embed=total_embed, view=view, ephemeral=True
                    )
                # elif item not in data:
                #     await interaction.response.send_message(
                # "Cant find a token with that ticker.",ephemeral=True)

                except Exception as e:
                    print(e)


async def setup(bot):
    await bot.add_cog(Total(bot))
