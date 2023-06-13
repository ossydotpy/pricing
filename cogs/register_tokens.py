import json
from discord.ext import commands
from functions.custom_functions import logging_setup


class AddTokenCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tokenregistrylog = logging_setup(f"logs/{__name__}.log",f"pricing.{__name__}")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def addtoken(self, ctx, token_name, token_hex, policy_id, pool_id, supply, image):
        if not self.validate_inputs(token_name, token_hex, policy_id, pool_id, supply, image):
            await ctx.send("Invalid input. Please provide all the required information.")
            self.tokenregistrylog.warn("missing arguments")
            return

        token_data = {
            "token_hex": token_hex,
            "policy_id": policy_id,
            "pool_id": pool_id,
            "supply": supply,
            "image": image
        }

        try:
            with open("verified_tokens.json", "r+") as file:
                data = json.load(file)
                data[0][token_name] = token_data  # Add the new token to the existing dictionary
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()
        except (IOError, json.JSONDecodeError) as e:
            await ctx.send("Error occurred while adding the token.")
            self.tokenregistrylog.error(e)
            return

        await ctx.send(f"Token '{token_name}' has been added to the verified tokens.")

    def validate_inputs(self, token_name, token_hex, policy_id, pool_id, supply, image):
        if not all([token_name, token_hex, policy_id, pool_id, supply, image]):
            return False
        return True

    @commands.command(hidden=True)
    @commands.is_owner()
    async def updatetoken(self, ctx, token_name, parameter, new_value):
        try:
            with open("verified_tokens.json", "r+") as file:
                data = json.load(file)
                if token_name in data[0]:
                    token_details = data[0][token_name]
                    if parameter in token_details:
                        token_details[parameter] = new_value
                        file.seek(0)
                        json.dump(data, file, indent=4)
                        file.truncate()
                        await ctx.send(f"Token '{token_name}' has been updated.")
                    else:
                        await ctx.send(f"Invalid field '{parameter}' for token '{token_name}'.")
                else:
                    await ctx.send(f"Token '{token_name}' does not exist.")
        except (IOError, json.JSONDecodeError) as e:
            await ctx.send("Error occurred while updating the token.")
            self.tokenregistrylog.error(e)


    @commands.command(hidden=True)
    @commands.is_owner()
    async def deletetoken(self, ctx, token_name):
        try:
            with open("verified_tokens.json", "r+") as file:
                data = json.load(file)
                if token_name in data[0]:
                    del data[0][token_name]  # Delete the token from the dictionary
                    file.seek(0)
                    json.dump(data, file, indent=4)
                    file.truncate()
                    await ctx.send(f"Token '{token_name}' has been deleted.")
                else:
                    await ctx.send(f"Token '{token_name}' does not exist.")
        except (IOError, json.JSONDecodeError) as e:
            await ctx.send("Error occurred while deleting the token.")
            self.tokenregistrylog.error(e)

async def setup(bot):
    await bot.add_cog(AddTokenCommand(bot))
