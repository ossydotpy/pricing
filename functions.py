import requests
import json

def get_trading_history(policy_id: str, token_name: str, interval: str):
    url = "https://analyticsv2.muesliswap.com/price"
    params = {
        "policy-id": policy_id,
        "tokenname": token_name,
        "interval": interval
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        with open("historical_data.json","w") as f:
            json.dump(data,f)
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def get_all_pairs():
    url = 'https://api-mainnet-prod.minswap.org/coinmarketcap/v2/pairs'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        with open("all_pairs.json","w") as f:
            json.dump(data,f)
    else:
        print(f"Error: {response.status_code}")


def get_recent_trades(token_policy:str):

    url=f'http://analyticsv2.muesliswap.com/trades/{token_policy}.ADA'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        with open("recent_trades.json","w") as f:
            json.dump(data,f)
    else:
        print(f"Error: {response.status_code}")


def get_token_volume(policy_id,token_name):
    url = "https://analyticsv2.muesliswap.com/volume"
    params = {
        "policy-id": policy_id,
        "tokenname": token_name,
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        with open("volume_data.json","w") as f:
            json.dump(data,f)
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None