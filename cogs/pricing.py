import discord
from discord import app_commands
from discord.ext import commands
from buttons import Buttons
import json
import datetime
from decimal import Decimal
import asyncio

import minswap.assets as minas
import minswap.pools as pools

class PriceCog(commands.Cog):
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

    @app_commands.command(name="price_of")
    async def price_of(self, interaction: discord.Interaction, ticker: str):
        """check the price of your tokens"""
        await interaction.response.defer()
        token_info = self.get_token_info(ticker.upper())
        if not token_info:
            await interaction.followup(f"Invalid ticker: ${ticker.upper()}",ephemeral=True)
        # token_hex = token_info["token_hex"]
        # policy_id = token_info["policy_id"]
        pool_id = token_info["pool_id"]
        # pool_plus_hex = policy_id+token_hex

        try:
            pool = pools.get_pool_by_id(pool_id=pool_id)

            decimals =Decimal(10 ** minas.asset_decimals(pool.unit_b))
            locked, minted = minas.circulating_asset(pool.unit_b)

            circulating = Decimal(minted.quantity() - locked.quantity()) / decimals
            token_ada_price = pool.price[0]
            marketcap = token_ada_price * circulating
            diluted_cap = token_ada_price * minted.quantity()

            price_embed = discord.Embed(
                title=f"Results for ${ticker}.",
                color=discord.Color.from_rgb(102, 255, 51),
                timestamp=datetime.datetime.utcnow(),
            )
            price_embed.add_field(
                name="Current Price", value=f"{token_ada_price:,.10f} ADA", inline=False
            )
            price_embed.add_field(name="░░░░░░░░░░░░░░░░░░░░░░░░░░░", value="")
            price_embed.add_field(
                name="Totoal Supply", value=f"{minted.quantity():,.0f}", inline=False
            )
            price_embed.add_field(
                name="Circulating Supply", value=f"{circulating:,.0f}", inline=False
            )
            price_embed.add_field(
                name="Current MarketCap", value=f"{marketcap:,.0f} ADA", inline=False
            )
            price_embed.add_field(
                name="Diluted MarketCap", value=f"{diluted_cap:,.0f} ADA", inline=False
            )
            price_embed.set_footer(
                text="like this, sponsor me $gimmeyourada",
            )
            view=Buttons()
            view.add_item(discord.ui.Button(label="Report",style=discord.ButtonStyle.link,url="https://discordapp.com/users/638340154125189149"))

            
            await asyncio.sleep(6)
            await interaction.followup.send(embed=price_embed,view=view)
        except Exception as e:
            print(f"Error in price_check: {e}")
            
            await interaction.response.send_message(
                "An error occurred while fetching the price. Please try again later.",ephemeral=True
            )

            


async def setup(bot):
    await bot.add_cog(PriceCog(bot),)
                    #    guilds=[discord.Object(id=1096587951586164756)])
