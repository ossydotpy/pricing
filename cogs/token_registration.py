import discord
import json
from discord.ext import commands


class RegistrationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.registered_users = set()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if isinstance(message.channel, discord.DMChannel):
            if message.content.lower() == "register":
                if message.author.id not in self.registered_users:
                    self.registered_users.add(message.author.id)
                    await self.register_user(message.author)
                    await message.author.send(
                        "Please answer the following questions to complete your registration:"
                    )
                    # await self.prompt_questions(message.author)

    async def register_user(self, user):
        questions = [
            ("Enter the token name", "token_name"),
            ("Enter the token hex", "token_hex"),
            ("Enter the policy ID", "policy_id"),
            ("Enter the pool ID", "pool_id"),
            ("Enter the supply", "supply"),
            ("Enter the image URL", "image"),
        ]
        user_responses = {}
        for question, key in questions:
            response = await self.ask_question(user, question)
            user_responses[key] = response

        with open("registered_users.json", "a") as file:
            if file.tell() != 0:
                file.write(",\n")
            json.dump(user_responses, file)

    async def ask_question(self, user, question):
        await user.send(question)
        response = await self.bot.wait_for("message", check=lambda m: m.author == user)
        return response.content

    @commands.command()
    async def status(self, ctx):
        await ctx.send(
            "Registration is open. Send me a DM with 'register' to start the process."
        )


async def setup(bot):
    await bot.add_cog(RegistrationCog(bot))
