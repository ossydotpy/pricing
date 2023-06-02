import os
import logging
from decimal import Decimal
from dotenv import load_dotenv
import aiohttp,requests
from jsonschema import validate



# logging setup
def logging_setup(log_file, log_name):
    # Create the logger and set its level
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    # Create the file handler
    handler = logging.FileHandler(log_file,encoding='utf-8', errors='ignore')

    # Create the formatter and add it to the handler
    dt_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", dt_fmt, style="{")
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger

handle_log = logging_setup("logs/main.log","pricing.handle")

load_dotenv()
handle_policy_id = "f0ff48bbb7bbe9d59a40f1ce90e9e9d0ff5002ec48f232b49ca0fb9a"
header = {"PROJECT_ID":os.getenv("PROJECT_ID")}
base_url = "https://cardano-mainnet.blockfrost.io/api/v0/"

# send api requests asynchronously
async def send_api_request(apiurl, headers=None, params = None):
    async with aiohttp.ClientSession() as session:
      async with session.get(apiurl, headers=headers) as response:
        data = await response.json()
        return data, response.status

# resolve adahandle
async def resolve_handle(handle):
    handle = handle.lower()
    hexcode = ''.join('{:02x}'.format(ord(c)) for c in str(handle))
    address_url = f"{base_url}assets/{handle_policy_id}{hexcode}/addresses"
    response =  requests.get(url=address_url, headers=header)
    if response.status_code == 200:
       address_response = response.json()
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


# resolve address to stake 
async def resolve_address(address):
    url = f"{base_url}addresses/{address}"
    response, status = await send_api_request(url,headers=header)
    if status == 200:
        stake = response["stake_address"]
        return stake
    else:
        handle_log.info("couldnt resolve user stake address")
        return None

# validate api response with schema file
def validate_json_schema(api_response, schemafile):
    try:
        validate(api_response, schema=schemafile)
        return True
    except Exception as e:
        return None
    
# get cardano price
def get_cardano_usd_price():
    res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=cardano&vs_currencies=usd").json()
    return Decimal(res["cardano"]["usd"])