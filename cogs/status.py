import discord
import asyncio
from discord.ext import commands, tasks
import minswap.assets as minas
import minswap.pools as pools
import locale
from decimal import Decimal, ROUND_HALF_UP

locale.setlocale(locale.LC_ALL, "")
import json


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
    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def watch(self, ctx, ticker: str):
        with open("verified_tokens.json", "r") as f:
            tokens = json.load(f)
            if ticker.upper() in tokens[0]:
                self.ticker = ticker.upper()
                self.load_tokens()
                await ctx.send(
                    f"bot is now monitoring ${self.ticker} price.\nPlease wait a minute or two for price to sync.\nThanks:)"
                )
            else:
                await ctx.send(
                    f"Could not find {ticker.upper()} in the veried tokens ."
                )

    # update the bot's status every 10 seconds
    @tasks.loop(seconds=10)
    async def update_status(self):
        try:
            token_to_ada_price = pools.get_pool_by_id(pool_id=self.pool_id).price[0].quantize(Decimal('0.0000000001'), rounding=ROUND_HALF_UP)
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
                    name=f"{price_change} ${self.ticker} price: {token_to_ada_price} ADA",
                )
                await self.bot.change_presence(activity=activity)
            else:
                activity = discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"Error fetching price for {self.ticker}",
                )
                await self.bot.change_presence(activity=activity)
        except Exception as e:
            print(f"Error in update_status: {e}")
        await asyncio.sleep(60)


async def setup(bot):
    await bot.add_cog(StatusCog(bot))
