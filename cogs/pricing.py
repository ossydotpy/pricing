import discord
import json
import datetime
from discord.ext import commands
import minswap.assets as minas
import minswap.pools as pools
import locale
from decimal import Decimal, ROUND_HALF_UP

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
    async def price_of(self, ctx, ticker: str):
        token_info = self.get_token_info(ticker.upper())
        if not token_info:
            await ctx.send(f"Invalid ticker: ${ticker.upper()}")
            return

        token_hex = token_info["token_hex"]
        policy_id = token_info["policy_id"]
        pool_id = token_info["pool_id"]
        supply= Decimal(token_info["supply"])
        # pool_plus_hex = policy_id+token_hex

        try:
            token_ada_price = pools.get_pool_by_id(pool_id=pool_id).price[0]
            marketcap = token_ada_price*supply
            
            price_embed = discord.Embed(title=f"{ticker} price", color=discord.Color.from_rgb(102, 255, 51),timestamp=datetime.datetime.utcnow())
            price_embed.add_field(name="Current Price", value=f"{token_ada_price.quantize(Decimal('0.0000000001'), rounding=ROUND_HALF_UP)} ADA",inline=False)
            price_embed.add_field(name="░░░░░░░░░░░░░░░░░░░░░░░░░░░░", value="")
            price_embed.add_field(name="Current MarketCap", 
                                  value=f"{locale.currency(marketcap,grouping=True).replace(locale.localeconv()['currency_symbol'], '')} ADA",
                                  inline=False)
            await ctx.send(embed=price_embed)
        except Exception as e:
            print(f"Error in price_check: {e}")
            await ctx.send("An error occurred while fetching the price. Please try again later.")

async def setup(bot):
    await bot.add_cog(PriceCog(bot))
