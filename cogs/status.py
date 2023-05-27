import discord
import asyncio
from discord import app_commands
from discord.ext import commands, tasks
import minswap.assets as minas
import minswap.pools as pools
import locale

locale.setlocale(locale.LC_ALL, "")
import json

from functions.custom_functions import logging_setup

status_log = logging_setup(f"logs/{__name__}.log",f"pricing.{__name__}")

class StatusCog(commands.Cog):
    def __init__(self, bot, pool_id=None, policy_id=None, token_hex=None, ticker=None):
        self.bot = bot
        self.pool_id = (
            pool_id
            or "3dfeaac38108417e2dc7aedb6cb33d7b7b36400b0529d90cc98a539f255697a0"
        )
        self.policy_id = (
            policy_id or "dbc31b04d90b37332813cb4cee3e8f79994643d899a5366797e745ee"
        )
        self.token_hex = token_hex or "465544"
        self.pool_plus_hex = self.policy_id + self.token_hex
        self.ticker = ticker or minas.asset_ticker(self.pool_plus_hex)

        self.last_price = None
        self.update_status.start()

    # load tokens from JSON file
    def load_tokens(self):
        with open("verified_tokens.json", "r") as f:
            tokens = json.load(f)
            for ticker, info in tokens[0].items():
                if ticker.upper() == self.ticker:
                    self.pool_id = info["pool_id"]
                    self.policy_id = info["policy_id"]
                    self.token_hex = info["token_hex"]
                    self.pool_plus_hex = self.policy_id + self.token_hex

    # set the token to watch
    @app_commands.command(name="watch")
    @app_commands.checks.has_permissions(manage_messages = True)
    async def watch(self, interaction: discord.Interaction, ticker: str):
        """set discord bot status"""
        await interaction.response.defer(ephemeral=True)
        try:
            with open("verified_tokens.json", "r") as f:
                tokens = json.load(f)
        except Exception as e:
            await interaction.followup.send("server side error try again later")
            status_log.error(f"loading verified tokens: {e}")
            return
        if ticker.upper() in tokens[0]:
            self.ticker = ticker.upper()
            self.load_tokens()
            await interaction.followup.send(
                f"bot is now monitoring ${self.ticker} price.\nPlease wait a minute or two for price to sync.\nThanks:)"
            )
            status_log.info(f"{interaction.user.name}-{interaction.user.id} has set status to {self.ticker}")
        else:
            await interaction.followup.send(
                f"Could not find {ticker.upper()} in the veried tokens ."
            )
        

    # update the bot's status every 10 seconds
    @tasks.loop(seconds=20)
    async def update_status(self):
        try:
            pool = pools.get_pool_by_id(self.pool_id)
            token_to_ada_price = pool.price[0]
            if self.last_price is not None:
                if token_to_ada_price > self.last_price:
                    price_change = "🔺"
                elif token_to_ada_price < self.last_price:
                    price_change = "🔻"
                else:
                    price_change = "🔹"
            else:
                price_change = ""
            self.last_price = token_to_ada_price

            if self.ticker:
                activity = discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"{price_change} ${self.ticker} price: {token_to_ada_price:,.8f} ADA",
                )
                await self.bot.change_presence(activity=activity)
            else:
                activity = discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"Error fetching price for {self.ticker}",
                )
                await self.bot.change_presence(activity=activity)
                status_log.warning("error in fetching price for status")
        except Exception as e:
            status_log.error(f"Error in update_status: {e}")
        await asyncio.sleep(60)


async def setup(bot):
    await bot.add_cog(StatusCog(bot))
    #    guilds=discord.Object.id=1096587951586164756)
