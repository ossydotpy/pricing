import discord
import json
from decimal import Decimal
from discord.ext import commands
import minswap.assets as minas
import minswap.pools as pools
import locale

class PriceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.token_dict = {}

        with open('verified_tokens.json') as tokens:
            data = json.load(tokens)
            for info in data:
                for ticker, info in info.items():
                    self.token_dict[ticker] = info

    def get_token_info(self, ticker):
        if ticker in self.token_dict:
            return self.token_dict[ticker]
        else:
            return None

    @commands.command()
    async def price_check(self, ctx, ticker: str):
        token_info = self.get_token_info(ticker.upper())
        if not token_info:
            await ctx.send(f"Invalid ticker: ${ticker.upper()}")
            return

        token_hex = token_info["token_hex"]
        policy_id = token_info["policy_id"]
        pool_id = token_info["pool_id"]
        pool_plus_hex = policy_id+token_hex


        try:
            pool_result = pools.get_pool_by_id(pool_id=pool_id).price
            ada_to_token_price = float(pool_result[0])

            supply = Decimal(minas.get_asset_info(pool_plus_hex).quantity)
            marketcap = int(ada_to_token_price*supply)
            
            price_embed = discord.Embed(title=f"{ticker} price")
            price_embed.add_field(name="Current Price", value=f"{ada_to_token_price} ADA",inline=False)
            price_embed.add_field(name="Current MarketCap", 
                                  value=f"{locale.currency(marketcap,grouping=True).replace(locale.localeconv()['currency_symbol'], '')} ADA",
                                  inline=False)
            price_embed.set_footer(text="requested at time here")
            await ctx.send(embed=price_embed)
        except Exception as e:
            print(f"Error in price_check: {e}")
            await ctx.send("An error occurred while fetching the price. Please try again later.")


async def setup(bot):
    await bot.add_cog(PriceCog(bot))
