from urllib.parse import urlencode
import discord
from discord import app_commands
from discord.ext import commands
from buttons import Buttons
import json
import datetime
from decimal import Decimal
import aiohttp

import minswap.assets as minas
import minswap.pools as pools


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
            print(f"An error occurred during the API request: {e}")
            return None, None

    @app_commands.command(name="price_of")
    @commands.cooldown(rate=1, per=60.0)
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


        try:
            pool = pools.get_pool_by_id(pool_id=pool_id)
           
            tvl = pool.tvl

            decimals = Decimal(10 ** minas.asset_decimals(pool.unit_b))
            locked, minted = minas.circulating_asset(pool.unit_b)

            circulating = Decimal(minted.quantity() - locked.quantity()) / decimals
            token_ada_price = pool.price[0]
            marketcap = token_ada_price * circulating


            params = {
                "currencySymbolA": "",
                "tokenNameA": "",
                "currencySymbolB": token_info["policy_id"],
                "tokenNameB": token_info["token_hex"],
            }

            minswap_link = "https://app.minswap.org/swap?" + urlencode(params)

            volume_data = self.load_snapshot()
            if volume_data:
                for item in volume_data.values():
                    if pool_id in item["pool_id"]:
                        daily_volume = float(item["quote_volume"])


                price_embed = discord.Embed(
                    title=f"Results for ${ticker}.",
                    color=discord.Color.from_rgb(102, 255, 51),
                    timestamp=datetime.datetime.utcnow(),
                )
                price_embed.add_field(
                    name="Current Price",
                    value=f"{token_ada_price:,.10f} ₳",
                    inline=False,
                )
                price_embed.add_field(
                    name="Daily Volume", value=f"{(daily_volume):,.02f} ₳", inline=False
                )
                price_embed.add_field(
                    name="Current MarketCap", value=f"{marketcap:,.0f} ₳"
                )
                price_embed.add_field(name="TVL", value=f"{tvl:,.0f} ₳")
                price_embed.set_footer(
                    text="like this?\nsponsor me: $gimmeyourada",
                )

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
                    )
                )

                # await asyncio.sleep(3)
                await interaction.followup.send(
                    embed=price_embed, view=view, ephemeral=True
                )
            else:
                await interaction.followup.send(
                   file=discord.File("src/img/on_error.png"), ephemeral=True
                )
                # print(status)
                return

        except Exception as e:
            await interaction.followup.send(
                file=discord.File("exceptio"), ephemeral=True
            )
            print(f"Error in price_check: {e.with_traceback()}")
            return


async def setup(bot):
    await bot.add_cog(
        TokenInfo(bot),
    )
