import json
from discord.ext import commands
from logfn import logging_setup

addtokenlog = logging_setup("logs/register_tokens.log","pricing.register_tokens")

class AddTokenCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def addtoken(self, ctx, token_name, token_hex, policy_id, pool_id, supply, image):
        if not self.validate_inputs(token_name, token_hex, policy_id, pool_id, supply, image):
            await ctx.send("Invalid input. Please provide all the required information.")
            addtokenlog.warn("missing arguments")
            return

        record = {
            token_name: {
                "token_hex": token_hex,
                "policy_id": policy_id,
                "pool_id": pool_id,
                "supply": supply,
                "image": image
            }
        }

        try:
            with open("verified_tokens.json", "r+") as file:
                data = json.load(file)
                data.append(record)
                file.seek(0)
                json.dump(data, file, indent=4)
        except (IOError, json.JSONDecodeError) as e:
            await ctx.send("Error occurred while adding the token.")
            addtokenlog.error(e)
            return

        await ctx.send(f"Token '{token_name}' has been added to the verified tokens.")

    def validate_inputs(self, token_name, token_hex, policy_id, pool_id, supply, image):
        if not all([token_name, token_hex, policy_id, pool_id, supply, image]):
            return False
        return True

async def setup(bot):
    await bot.add_cog(AddTokenCommand(bot))
