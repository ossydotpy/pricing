import re
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands

import os
from datetime import datetime

import json
from urllib.parse import urlencode
from decimal import Decimal

from functions.buttons import Buttons

import minswap.pools as pools
import minswap.assets as minas

import functions.custom_functions as functions
from functions.custom_functions import logging_setup

wallet_stats_log = logging_setup(f"logs/{__name__}.log",f"pricing.{__name__}")

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

  def cooldown_for_everyone_but_me(
    interaction: discord.Interaction, ) -> Optional[app_commands.Cooldown]:
    if interaction.user.id == 638340154125189149:
      return None
    return app_commands.Cooldown(1, 180.0)

  @app_commands.command(name="how_many")
  @app_commands.checks.dynamic_cooldown(cooldown_for_everyone_but_me)
  @app_commands.describe(
    ticker="token name",
    address="$adahandle or Cardano Stake Address",
    hide="Chooose whether you alone or whole chat sees your results")
  async def how_many(self, interaction: discord.Interaction, ticker: str,
                     address: str, hide: bool):
    """
        Checks how many tokens held by any adahandle or stake address.
        input ticker and any $adahandle or stake address to begin.
        if one doesn't work try the other.
        """
    await interaction.response.defer(ephemeral= hide)

    userinput = address if address.startswith('$') else (f"{address[:10]}...{address[-4:]}" if address.startswith('stake') else (address[:15]))

    # validate stake address starts with "stake"
    if not address.startswith(("stake", "$", "addr")):
      await interaction.followup.send(
        "please use a valid Ada Handle or Stake key format", ephemeral=True)
      return


    token_info = self.get_token_info(ticker.upper())
    if not token_info:
      await interaction.followup.send(f"Invalid ticker: ${ticker.upper()}", ephemeral=True)
      return
    
    # resolve the handle name
    if re.match(r"^\$.+",address):
      stripped_handle = address.strip("$")
      address =  await functions.resolve_handle(stripped_handle)
    elif re.match(r"^addr.+",address):
      address = await functions.resolve_address(address)

    asset_image = str(token_info["image"])
    asset_name = str(
      token_info["policy_id"] +
      token_info["token_hex"])  # name of assets as stored on the chain
    pool_id = token_info["pool_id"]
    pool = pools.get_pool_by_id(pool_id=pool_id)
    price = pool.price[0]
    decimals = Decimal(10 ** minas.asset_decimals(pool.unit_b))
    locked, minted = minas.circulating_asset(pool.unit_b)
    circulating_supply = Decimal(minted.quantity() - locked.quantity()) / decimals

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
        response, status_code = await functions.send_api_request(apiurl=url,headers=self.header)
    else:
      await interaction.followup.send("unable to resolve that address")
      return

    if status_code == 200:
      json_response = response
    else:
      await interaction.followup.send(
        f"Please check the wallet you  provided!\nerror code {status_code}")
      return
    schema = self.get_schema()
    # resonse validation
    if functions.validate_json_schema(json_response, schemafile=schema) is not None:
      found_assets = []  # List to store the found assets

      for item in json_response:
        unit = item["unit"]
        amount = Decimal(item["quantity"])/decimals

        if asset_name in str(unit):
          found_assets.append(
            (unit, amount))  # Add the found asset to the list

      if found_assets:
        ada_usd = functions.get_cardano_usd_price()
        total_embed = discord.Embed(
          title=f"${ticker.upper()} held by\n{userinput}")
        total_embed.add_field(name="Token",
                              value=f"${ticker.upper()}",
                              inline=False)

        for unit, amount in found_assets:
          total_embed.add_field(name=f"Amount Held",
                                value=f"{float(amount):,.2f} ${ticker.lower()}",
                                inline=True)
          
        total_embed.add_field(
          name="Percentage Held",
          value=f"~ ({float((amount*100)/circulating_supply):,.4f} %)",
          inline=False,
        )
        total_embed.add_field(
          name="Value (ADA)",
          value=f"{price * Decimal(amount):,.2f} ₳.",
          inline=False,
        )
        total_embed.add_field(
          name="Value (USD)",
          value=f"${price * Decimal(amount)* ada_usd:,.2f}.",
          inline=False,
        )
        total_embed.set_thumbnail(url=asset_image)
        total_embed.set_footer(
          text=f"requested by {interaction.user.name} at {datetime.now()}")
        view = Buttons()
        view.add_item(
          discord.ui.Button(
            label=f"Buy more ${ticker.upper()} on Minswap",
            style=discord.ButtonStyle.url,
            url=minswap_link,
            emoji="<:mincat_blue:849414479866757171>",
          ))
        view.add_item(
          discord.ui.Button(
          label="Support",
          style=discord.ButtonStyle.link,
          url="https://discord.gg/2sUZ3YShm6",
          emoji="<:transparentlogo:1114079453258203187>",
          row=2,
          )
        )
        # await asyncio.sleep(1)
        await interaction.followup.send(embed=total_embed,
                                        view=view,
                                        ephemeral=True)
        return
      else:
        wallet = "stakekey"
        await interaction.followup.send(
          f"No `${ticker}` found in `{userinput}`.\nDid we get that wrong?:heart:\nTry again with a different handle/stakekey/address.",
          ephemeral=True,
        )
        return
    else:
      # await asyncio.sleep(1)
      await interaction.followup.send("make sure you submitted a valid $adahandle or stakeKey.",
                                      ephemeral=True)
      return


async def setup(bot):
  await bot.add_cog(WalletStat(bot))