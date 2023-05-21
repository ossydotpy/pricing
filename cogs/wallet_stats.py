import re
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

import os
from datetime import datetime

import json
import jsonschema
from jsonschema import validate

import aiohttp
import requests
from urllib.parse import urlencode
from decimal import Decimal

from buttons import Buttons

import minswap.assets as minas
import minswap.pools as pools

from logfn import logging_setup
from resolve_ada_handle import resolve_handle

wallet_stats_log = logging_setup("logs/wallet_stats.log","pricing.wallet_stats")

class WalletStat(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.header = {"PROJECT_ID":os.getenv("PROJECT_ID")}
    self.token_dict = {}

    # load verified tokens
    with open("verified_tokens.json") as tokens:
      data = json.load(tokens)
      for info in data:
        for ticker, info in info.items():
          self.token_dict[ticker] = info

  # load json schema
  def get_schema(self):
    with open("stakeschema.json") as scheme:
      jsonscheme = json.load(scheme)
      return jsonscheme

  def get_token_info(self, ticker):
    if ticker in self.token_dict:
      return self.token_dict[ticker]
    else:
      return None

  # validate api response with schema file
  def validate_json_schema(self, api_response, schemafile):
    try:
      validate(api_response, schema=schemafile)
      return True
    except Exception as e:
      return None

  @staticmethod
  async def send_api_request(self, apiurl, headers=None):
    async with aiohttp.ClientSession() as session:
      async with session.get(apiurl, headers=headers) as response:
        data = await response.json()
        return data, response.status

  def cooldown_for_everyone_but_me(
    interaction: discord.Interaction, ) -> Optional[app_commands.Cooldown]:
    if interaction.user.id == 638340154125189149:
      return None
    return app_commands.Cooldown(1, 180.0)

  @app_commands.command(name="how_many")
  @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
  @app_commands.describe(
    ticker="token name",
    address="Ada Handle or Cardano Stake Address",
    hide="Chooose whether you alone or whole chat sees your results")
  async def how_many(self, interaction: discord.Interaction, ticker: str,
                     address: str, hide: bool):
    """
        Checks how many tokens held by any stake address
        input ticker and any stake address to begin.

        Choose `True` to hide your result.
        """
    await interaction.response.defer(ephemeral=hide)
    query_term = address
    # validate stake address starts with "stake"
    if not address.startswith(("stake", "$")):
      await interaction.followup.send(
        "please use a valid Ada Handle or Stake key format", ephemeral=True)
      return

    # resolve the handle name
    if re.match(r"^\$.+",address):
            stripped_address = address.strip("$")
            address =  await resolve_handle(stripped_address)

    token_info = self.get_token_info(ticker.upper())
    if not token_info:
      await interaction.followup.send(f"Invalid ticker: ${ticker.upper()}",
                                      ephemeral=True)
      return

    asset_name = str(
      token_info["policy_id"] +
      token_info["token_hex"])  # name of assets as stored on the chain
    pool_id = token_info["pool_id"]
    pool = pools.get_pool_by_id(pool_id=pool_id)
    price = pool.price[0]

    params = {
      "currencySymbolA": "",
      "tokenNameA": "",
      "currencySymbolB": token_info["policy_id"],
      "tokenNameB": token_info["token_hex"],
    }

    minswap_link = "https://app.minswap.org/swap?" + urlencode(params)

    if address is not None:
    # get assets in the stake address
        url = f"https://cardano-mainnet.blockfrost.io/api/v0/accounts/{address}/addresses/assets"
        response, status_code = await self.send_api_request(self,
                                                            apiurl=url,
                                                            headers=self.header)
    else:
      await interaction.followup.send("unable to resolve that address")
      return

    if status_code == 200:
      json_response = response
    else:
      await interaction.followup.send(
        "Please check the stake key you  provided!")
      return
    schema = self.get_schema()
    # resonse validation
    if self.validate_json_schema(json_response, schemafile=schema) is not None:
      found_assets = []  # List to store the found assets

      for item in json_response:
        unit = item["unit"]
        amount = item["quantity"]

        if asset_name in str(unit):
          found_assets.append(
            (unit, amount))  # Add the found asset to the list

      if found_assets:
        total_embed = discord.Embed(
          title=f"${ticker.upper()} held by\n{query_term}?")
        total_embed.add_field(name="Token",
                              value=f"${ticker.lower()}",
                              inline=False)

        for unit, amount in found_assets:
          total_embed.add_field(name=f"Amount Held",
                                value=f"{float(amount):,.2f}",
                                inline=True)
        total_embed.add_field(
          name="Estimated Value",
          value=f"{price * Decimal(amount):,.2f} ₳.",
          inline=True,
        )
        total_embed.set_footer(
          text=f"requested by {interaction.user.name} at {datetime.now()}")
        view = Buttons()
        view.add_item(
          discord.ui.Button(
            label=f"Buy more ${ticker} on Minswap",
            style=discord.ButtonStyle.url,
            url=minswap_link,
            emoji="<:mincat_blue:849414479866757171>",
          ))
        # await asyncio.sleep(1)
        await interaction.followup.send(embed=total_embed,
                                        view=view,
                                        ephemeral=True)
        return
      else:
        # await asyncio.sleep(1)
        await interaction.followup.send(
          f"No assets `${ticker}` found in the wallet provided",
          ephemeral=True,
        )
        return
    else:
      # await asyncio.sleep(1)
      await interaction.followup.send("make sure you used a proper stake key.",
                                      ephemeral=True)
      return


async def setup(bot):
  await bot.add_cog(WalletStat(bot))
