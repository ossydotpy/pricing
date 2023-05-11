import discord
from discord import app_commands
from discord.ext import commands

import os
import json
import requests
import asyncio
from urllib.parse import urlencode
from decimal import Decimal

from buttons import Buttons

import minswap.assets as minas
import minswap.pools as pools


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
    @app_commands.checks.cooldown(1,20)
    async def how_many(
        self, interaction: discord.Interaction, ticker: str, stake_addr: str
    ):
        """
        Checks how many tokens held by any stake address
        input ticker and any stake address to begin
        """
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

        pool_id = token_info["pool_id"]
        pool = pools.get_pool_by_id(pool_id=pool_id)
        price = pool.price[0]

        params = {
            "currencySymbolA": "",
            "tokenNameA": "",
            "currencySymbolB": token_info["policy_id"],
            "tokenNameB": token_info["token_hex"],
        }
        minswap_link = "https://app.minswap.org/swap?" + urlencode(params)

        # get assets in the stake address
        url = f"https://cardano-mainnet.blockfrost.io/api/v0/accounts/{stake_addr}/addresses/assets"
        header = {"PROJECT_ID": os.getenv("PROJECT_ID")}
        response = requests.get(url=url, headers=header)
        data = response.json()


        # if not isinstance(data, list) or len(data) == 0 or not all(isinstance(item, dict) for item in data):
        #     await interaction.followup.send(content="use a single address stake please")
        #     raise ValueError("Unexpected JSON response structure")
        
        for item in data:
            if not isinstance(item, dict) or "unit" not in item or "quantity" not in item:
                await interaction.followup.send("invalid")

                # raise ValueError("Invalid JSON format. Each item in the response should be a dictionary with 'unit' and 'quantity' keys.")

        for item in data:
            unit = item["unit"]
            amount = item["quantity"]

            if asset in str(unit):
                total_embed = discord.Embed(
                    title=f"how many ${ticker.upper()} do you hold?"
                )
                total_embed.add_field(
                    name="Token", value=f"${ticker.lower()}", inline=False
                )
                total_embed.add_field(
                    name="Amount Held", value=f"{amount}", inline=False
                )
                total_embed.add_field(
                    name="Estimated Value",
                    value=f"{price*Decimal(amount):.2f} ₳.",
                    inline=False,
                )
                view = Buttons()
                view.add_item(
                    discord.ui.Button(
                        label=f"Buy more ${ticker} on Minswap",
                        style=discord.ButtonStyle.url,
                        url=minswap_link,emoji="<:mincat_blue:849414479866757171>"
                    )
                )

                try:
                    await asyncio.sleep(3)
                    await interaction.followup.send(
                        embed=total_embed, view=view, ephemeral=True
                    )
                except Exception as e:
                    print(e)

        # except TypeError:
        #     await interaction.followup.send(content="please use a single address stake")
            
            # else:
            #     await interaction.followup.send(content="nothing found")


async def setup(bot):
    await bot.add_cog(Total(bot))
