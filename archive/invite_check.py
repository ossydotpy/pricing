from discord.ext import commands
import csv

with open("premium_users.csv") as f:
    data = f.readlines()
premium_users = [line.strip() for line in data]


class InviteCheck(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.premium_users = self.load_premium_users()

    def load_premium_users(self):
        premium_users = []
        with open("premium_users.csv", newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                premium_users.append(int(row[0]))
        return premium_users

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if guild.owner_id in self.premium_users or await self.bot.is_owner(guild.owner):
            # bot is invited to a server owned by a premium user or the bot owner
            pass
        else:
            # remove bot from the server
            await guild.leave()

async def setup(bot):
    await bot.add_cog(InviteCheck(bot))
