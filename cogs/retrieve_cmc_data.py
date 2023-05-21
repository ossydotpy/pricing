import requests
import json
import logging, logging.handlers
from discord.ext import commands, tasks
from logfn import logging_setup
import asyncio

retrieval_log = logging_setup("logs/retrieval.log", "pricing.retrieval")

class RetrievalCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.retrieval_task.start()

    def cog_unload(self):
        self.retrieval_task.cancel()

    @tasks.loop(minutes=15.0)
    async def retrieval_task(self):
        try:
            response = requests.get('https://api-mainnet-prod.minswap.org/coinmarketcap/v2/pairs')
            if response.status_code == 200:
                data = response.json()
                with open('snapshot.json', 'w') as f:
                    json.dump(data, f)
                retrieval_log.info("Snapshot updated successfully")
            else:
                retrieval_log.error("Failed to retrieve data")
        except requests.exceptions.RequestException as e:
            retrieval_log.error(f"Request error: {e}")
        
        await asyncio.sleep(30 * 60)  # Delay for 30 minutes

    @retrieval_task.before_loop
    async def before_retrieval_task(self):
        await self.bot.wait_until_ready()


async def setup(bot):
  await bot.add_cog(RetrievalCog(bot))
