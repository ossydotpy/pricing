import discord
import asyncio
from discord.ext import commands, tasks
import minswap.assets as minas
import minswap.pools as pools
import locale

locale.setlocale(locale.LC_ALL, '')

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool_id = (
            "6aa2153e1ae896a95539c9d62f76cedcdabdcdf144e564b8955f609d660cf6a2"
        )
        self.policy_id = "29d222ce763455e3d7a09a665ce554f00ac89d2e99a1a83d267170c6"
        self.token_hex = "4d494e"
        self.pool_plus_hex = self.policy_id + self.token_hex

        self.ticker = minas.asset_ticker(self.pool_plus_hex)
        self.last_price = None

        self.update_status.start()

    def cog_unload(self):
        self.update_status.cancel()

    @tasks.loop(seconds=10)
    async def update_status(self):
        try:
            pool_result = pools.get_pool_by_id(pool_id=self.pool_id).price
            ada_to_token_price = float(pool_result[0])

            if self.last_price is not None:
                if ada_to_token_price > self.last_price:
                    price_change = "📈"
                elif ada_to_token_price < self.last_price:
                    price_change = "📉"
                else:
                    price_change = ""
            else:
                price_change = ""
            self.last_price = ada_to_token_price

            if self.ticker:
                activity = discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"{price_change} ${self.ticker} price: {ada_to_token_price} ADA",
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

    
    @update_status.before_loop
    async def before_update_status(self):
        await self.bot.wait_until_ready()




async def setup(bot):
    await bot.add_cog(StatusCog(bot))
