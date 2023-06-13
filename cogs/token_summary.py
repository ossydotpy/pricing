import json
import asyncio
import math
import discord
from discord.ext import commands
from functions.custom_functions import send_api_request

class TrendList(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.url="https://api.coinmarketcap.com/dexer/v3/platformpage/trending-pairs?platform=29"

    @commands.command(name="trending")
    async def trending(self, ctx, page=1):
        """
        Show trending Cardano tokens from all DEXes.
        """
        result, status = await send_api_request(apiurl=self.url)

        if status == 200:
            tokens_per_page = 5
            total_tokens = len(result["data"])
            total_pages = math.ceil(total_tokens / tokens_per_page)
            start_index = (page - 1) * tokens_per_page
            end_index = start_index + tokens_per_page
            tokens = result["data"][start_index:end_index]

            trend_embed = discord.Embed(title="Trending Tokens from All Cardano DEXes", color=discord.Color.green())
            for i, item in enumerate(tokens, start=start_index + 1):
                arrow = "↗" if float(item['baseChange24h']) > 0 else "↘"
                deet = f'{i}. {item["baseTokenSymbol"]}/{item["quotoTokenSymbol"]} - {float(item["priceQuote"]):,.08f} - 24h({float(item["baseChange24h"])*100:,.02f}%) {arrow}'
                trend_embed.add_field(name="", value=f"{deet}", inline=False)

            trend_embed.set_thumbnail(url="https://i.ibb.co/rvTpW2X/logo.png")
            trend_embed.set_footer(text=f"Page {page}/{total_pages}")

            message = await ctx.send(embed=trend_embed)
            if total_pages > 1:
                await message.add_reaction('⬅️')
                await message.add_reaction('➡️')

                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️']

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                    if str(reaction.emoji) == '⬅️' and page > 1:
                        await message.delete()
                        await self.trending(ctx, page=page - 1)
                    elif str(reaction.emoji) == '➡️' and page < total_pages:
                        await message.delete()
                        await self.trending(ctx, page=page + 1)

                except asyncio.TimeoutError:
                    pass

                await message.clear_reactions()
        else:
            print("Error")

async def setup(bot):
    await bot.add_cog(TrendList(bot))