from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

import os
from datetime import datetime

import json
import jsonschema
from jsonschema import validate

import requests
import asyncio
from urllib.parse import urlencode
from decimal import Decimal

from buttons import Buttons


import minswap.assets as minas
import minswap.pools as pools


class WalletStat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token_dict = {}

        # load verified tokens
        with open("verified_tokens.json") as tokens:
            data = json.load(tokens)
            for info in data:
                for ticker, info in info.items():
                    self.token_dict[ticker] = info

        # load json schema

    def get_schema(self):
        with open("stakeschema.json") as scheme:
            jsonscheme = json.load(scheme)
            return jsonscheme

    def get_token_info(self, ticker):
        if ticker in self.token_dict:
            return self.token_dict[ticker]
        else:
            return None

    # validate api response with schema file
    def validate_json_schema(self, api_response, schemafile):
        try:
            validate(api_response, schema=schemafile)
            return True
        except Exception as e:
            return None

    def cooldown_for_everyone_but_me(
        interaction: discord.Interaction,
    ) -> Optional[app_commands.Cooldown]:
        if interaction.user.id == 638340154125189149:
            return None
        return app_commands.Cooldown(1, 1800.0)

    @app_commands.command(name="how_many")
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def how_many(
        self, interaction: discord.Interaction, ticker: str, stake_addr: str
    ):
        """
        Checks how many tokens held by any stake address
        input ticker and any stake address to begin
        """
        await interaction.response.defer()
        # validate stake address starts with "stake"
        if not stake_addr.startswith("stake"):
            await interaction.followup.send(
                "please use a stake key only", ephemeral=True
            )

        token_info = self.get_token_info(ticker.upper())
        if not token_info:
            await interaction.followup.send(
                f"Invalid ticker: ${ticker.upper()}", ephemeral=True
            )
            return

        asset_name = str(
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
        json_response = response.json()
        schema = self.get_schema()
        # resonse validation
        if self.validate_json_schema(json_response, schemafile=schema) is not None:
            found_assets = []  # List to store the found assets
            # Variable to store the total amount

            for item in json_response:
                unit = item["unit"]
                amount = item["quantity"]

                if asset_name in str(unit):
                    found_assets.append(
                        (unit, amount)
                    )  # Add the found asset to the list

            if found_assets:
                total_embed = discord.Embed(
                    title=f"${ticker.upper()} held by\n{stake_addr}?"
                )
                total_embed.add_field(
                    name="Token", value=f"${ticker.lower()}", inline=False
                )

                for unit, amount in found_assets:
                    total_embed.add_field(
                        name=f"Amount Held", value=f"{amount}", inline=False
                    )
                total_embed.add_field(
                    name="Estimated Value",
                    value=f"{price * Decimal(amount):.2f} ₳.",
                    inline=False,
                )
                total_embed.set_footer(
                    text=f"requested by {interaction.user.name} at {datetime.now()}"
                )
                view = Buttons()
                view.add_item(
                    discord.ui.Button(
                        label=f"Buy more ${ticker} on Minswap",
                        style=discord.ButtonStyle.url,
                        url=minswap_link,
                        emoji="<:mincat_blue:849414479866757171>",
                    )
                )
                asyncio.wait(1)
                await interaction.followup.send(
                    embed=total_embed, view=view, ephemeral=True
                )
            else:
                asyncio.wait(1)
                await interaction.followup.send(
                    f"No assets `${ticker}` found in the wallet provided",
                    ephemeral=True,
                )
        else:
            asyncio.wait(1)
            await interaction.followup.send(
                "make sure you used a proper stake key.", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(WalletStat(bot))