from discord.ext import commands
from logfn import logging_setup

admin_logs = logging_setup("logs/admin.log","pricing.admin")

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension: str):
        """load cogs"""
        try:
            await self.bot.load_extension(f"cogs.{extension}")
            await ctx.send(f"{extension} loaded!")
            admin_logs.info(f"{extension} loaded!")
            return
        except Exception as e:
            await ctx.send("error")
            admin_logs.error(f"error loading {extension} because {e}")
            return

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension: str):
        """unload cogs"""
        try:
            await self.bot.unload_extension(f"cogs.{extension}")
            await ctx.send(f"{extension} unloaded!")
            admin_logs.info(f"{extension} unloaded!")
            return
        except Exception as e:
            await ctx.send("error")
            admin_logs.error(f"error unloading {extension} because {e}")
            return

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, extension: str):
        """reload cogs"""
        try:
            await self.bot.reload_extension(f"cogs.{extension}")
            await ctx.send(f"{extension} reloaded!")
            admin_logs.info(f"{extension} reloaded!")
            return
        except Exception as e:
            await ctx.send("error")
            admin_logs.error(f"error reloading{extension} because {e}")
            return


async def setup(bot):
    await bot.add_cog(Admin(bot))

# commands.check()