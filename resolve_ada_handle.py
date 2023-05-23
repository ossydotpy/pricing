import aiohttp
import os
import re
import requests
from dotenv import load_dotenv
from logfn import logging_setup

handle_log = logging_setup("logs/main.log","pricing.handle")

load_dotenv()
handle_policy_id = "f0ff48bbb7bbe9d59a40f1ce90e9e9d0ff5002ec48f232b49ca0fb9a"
header = {"PROJECT_ID":os.getenv("PROJECT_ID")}
base_url = "https://cardano-mainnet.blockfrost.io/api/v0/"


async def send_api_request(apiurl, headers=None):
    async with aiohttp.ClientSession() as session:
      async with session.get(apiurl, headers=headers) as response:
        data = await response.json()
        return data, response.status

async def resolve_handle(handle):
    handle = handle.lower()
    hexcode = ''.join('{:02x}'.format(ord(c)) for c in str(handle))
    address_url = f"{base_url}assets/{handle_policy_id}{hexcode}/addresses"
    address_response =  requests.get(url=address_url, headers=header)
    if address_response.status_code == 200:
       address_response = address_response.json()
    else:
       handle_log.info("no address found for user handle")
       return None
    
    for data in address_response:
      handle_address = data["address"]

    stake_url = f"{base_url}addresses/{handle_address}"
    stake_response =  requests.get(url=stake_url, headers=header)
    if stake_response.status_code == 200:
       stake_response = stake_response.json()
       return stake_response["stake_address"]
    else:
       handle_log.info("couldnt resolve user stake address")
       return None

#test scenario
async def ss(address):
    if re.match(r"^\$",address):
        stripped_address = address.strip("$")
        stake_adress =  await resolve_handle(stripped_address)
        print(stake_adress)
    if stake_adress is not None:
       stake_url = f"{base_url}accounts/{stake_adress}/addresses/assets"
       response = requests.get(url=stake_url, headers=header)
       if response.status_code == 200:
          response = response.json()
          print(response)
    else:
      print("unable to resolve that address")
      return