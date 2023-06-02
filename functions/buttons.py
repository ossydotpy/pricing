import discord
from discord.ext import commands
from discord import ui
from discord.interactions import Interaction


class Buttons(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

class VerificationModal(ui.Modal,title="Enter Access Code"):
    code = ui.TextInput(label="Access Secret")

    @staticmethod
    def retrieve_tokens():
        with open("secrets.txt","r") as f:
            tokens = f.readlines()
        return tokens
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        role = discord.utils.get(interaction.guild.roles, name="testorrrr🤓")

        tokens= self.retrieve_tokens()
        for secret in tokens:
            if str(self.code.value) in secret.strip():
                tokens.remove(secret)
                await interaction.user.add_roles(role)
                await interaction.followup.send(f"role {role.name} granted",ephemeral=True)
                break
        else:
            await interaction.followup.send("Invalid Access Code", ephemeral=True)

        with open("secrets.txt", "w") as f:
            f.writelines(tokens)
