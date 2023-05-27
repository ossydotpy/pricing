from typing import Optional
from urllib.parse import urlencode
import discord
from discord import app_commands
from discord.ext import commands
from functions.buttons import Buttons
import json
import datetime
from decimal import Decimal
import aiohttp

import minswap.assets as minas
import minswap.pools as pools

from functions.custom_functions import logging_setup

price_check_log = logging_setup(f"logs/{__name__}.log",f"pricing.{__name__}")

class TokenInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
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
        
    def load_snapshot(self):
        with open("snapshot.json") as f:
            volume_data = json.load(f)
        return volume_data

    @staticmethod
    async def send_api_request(apiurl):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(apiurl) as response:
                    data = await response.json()
                    return data, response.status
        except aiohttp.ClientError as e:
            price_check_log.error(f"An error occurred during the API request: {e}")
            return None, None

    def cooldown_for_everyone_but_me(
        interaction: discord.Interaction,
    ) -> Optional[app_commands.Cooldown]:
        if interaction.user.id == 638340154125189149:
            return None
        return app_commands.Cooldown(1, 180.0)

    @app_commands.command(name="price_of")
    @app_commands.describe(ticker = "input the coin's ticker without the $ sign")
    @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
    async def price_of(self, interaction: discord.Interaction, ticker: str):
        """check the price of your tokens"""
        await interaction.response.defer()
        token_info = self.get_token_info(ticker.strip().upper())
        
        if not token_info:
            await interaction.followup.send(
                f"Invalid ticker: ${ticker.upper()}", ephemeral=True
            )
            return

        pool_id = token_info["pool_id"]
        token_image = token_info["image"]


        try:
            pool = pools.get_pool_by_id(pool_id=pool_id)
           
            tvl = pool.tvl

            decimals = Decimal(10 ** minas.asset_decimals(pool.unit_b))
            locked, minted = minas.circulating_asset(pool.unit_b)

            circulating = Decimal(minted.quantity() - locked.quantity()) / decimals
            token_ada_price = pool.price[0]
            marketcap = token_ada_price * circulating
            volume_data = self.load_snapshot()

        except Exception as e:
            await interaction.followup.send(
            "server errror! try again later", ephemeral=True)
            price_check_log.error(f"pool or cmc {e}")
            return

        params = {
            "currencySymbolA": "",
            "tokenNameA": "",
            "currencySymbolB": token_info["policy_id"],
            "tokenNameB": token_info["token_hex"],
        }

        minswap_link = "https://app.minswap.org/swap?" + urlencode(params)

        if volume_data:
            for item in volume_data.values():
                if pool_id in item["pool_id"]:
                    daily_volume = float(item["quote_volume"])


            price_embed = discord.Embed(
                title=f"Results for ${ticker}<:verified:1094013188200218634>",
                color=discord.Color.from_rgb(102, 255, 51),
                timestamp=datetime.datetime.utcnow(),
            )
            price_embed.add_field(
                name="Price",
                value=f"{token_ada_price:,.10f} ₳",
                inline=False,
            )
            price_embed.add_field(
                name="24h Volume", value=f"{(daily_volume):,.02f} ₳"
            )
            price_embed.add_field(
                name="Diluted M.Cap", value=f"{marketcap:,.0f} ₳"
            )
            price_embed.add_field(name="TVL", value=f"{tvl:,.0f} ₳")
            price_embed.set_footer(
                text="☕Buy me a coffee: \n$gimmeyourada",
            )
            # if ticker.lower() in ["min","snek"]:
            #     price_embed.add_field(name="",value=f"""side note:
            #     for {ticker}, take marketcap as the fully diluted marketcap because there is an error in calculating the circulating supply.""")
            # else:
            #     pass

            view = Buttons()
            view.add_item(
                discord.ui.Button(
                    label=f"Buy ${ticker} on minswap",
                    style=discord.ButtonStyle.green,
                    url=f"{minswap_link}",
                    emoji="<:mincat_blue:849414479866757171>",
                )
            )

            view.add_item(
                discord.ui.Button(
                    label="Report",
                    style=discord.ButtonStyle.link,
                    url="https://discordapp.com/users/638340154125189149",
                    row=2
                )
            )
            price_embed.set_thumbnail(url=token_image)

            await interaction.followup.send(
                embed=price_embed, view=view, ephemeral=True
            )
        else:
            await interaction.followup.send(
                file=discord.File("error sending embed."), ephemeral=True
            )
            price_check_log.error("error from embed side")
            return


async def setup(bot):
    await bot.add_cog(
        TokenInfo(bot)
    )
