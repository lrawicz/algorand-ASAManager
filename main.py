from typing import Union
from typing_extensions import Annotated
from fastapi import Depends, FastAPI,HTTPException,status
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod,indexer

import algosdk
import requests
import re
import json
import base64

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
#from algosdk.future import transaction


with open("config.json", "r") as config_file:
    config = json.load(config_file)
ownerPrivKey = mnemonic.to_private_key(config["mnemonic"])
ownerAddress = account.address_from_private_key(ownerPrivKey)
network = config["network"]["value"]
algod_client = algod.AlgodClient(config["network"]["apiToken"], config["network"][network]["node"])
indexer_client = indexer.IndexerClient(config["network"]["apiToken"], config["network"][network]["indexer"])

app = FastAPI()

#https://testnet-idx.algonode.cloud//v2/accounts/{account}

@app.get("/")
def index():
    
    return ({
        "appName":config['appName'],
        "version":config['version']
    })

@app.post("/create_asset")
def create_asset(fileName:str, hashString:str,token: Annotated[str, Depends(oauth2_scheme)]):
    return{"asd":token}
    hashString = "aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899"
    if (re.search("[^a-f0-9]",hashString) != None):
        raise HTTPException(status_code=422, detail="invalid hash data")
    hashBytes = bytes.fromhex("0001")

    urlNode = config["network"][network]["node"]
    apiToken = config["network"]["apiToken"]
    url = f"{urlNode}/v2/transactions/params"
    params = requests.get(url).json()
    suggestedParams = algosdk.transaction.SuggestedParams(
        fee=int(params["fee"]),
        first=int(params["last-round"]),
        last=int(params["last-round"]) + 1000,
        gh=params["genesis-hash"],
        gen=params["genesis-id"],
        consensus_version=params["consensus-version"],
        min_fee=params["min-fee"],
        )
    unsigned_tx = algosdk.transaction.AssetCreateTxn(
        sender=ownerAddress,
        sp = suggestedParams,
        total= 1,
        decimals= 0,
        default_frozen=True,
        manager=ownerAddress,
        reserve=ownerAddress,
        freeze=ownerAddress,
        clawback=ownerAddress,
        metadata_hash= hashBytes,
        unit_name="PDF_HASH",
        asset_name=fileName
    )
    signed_tx = unsigned_tx.sign(mnemonic.to_private_key(config["mnemonic"]))
    
    algod_client = algod.AlgodClient(apiToken, urlNode)  
    tx_id = algod_client.send_transaction(signed_tx)
    result ={
        "tx_id": tx_id
    }
    return result

@app.get("/find_asset")
async def find_ASA(fileName: Union[str,None] = None,hash: Union[str,None] = None):
    if hash == None and fileName == None:
        raise HTTPException(status_code=422, detail="variables hash and/or fileName should not be null")
    data = indexer_client.account_info(ownerAddress)["account"]
    assets =  [
        {
            "name":x["params"]["name"],
            "hash": "null" if "metadata-hash" not in x["params"] else base64.b64decode(x["params"]["metadata-hash"]).hex(),
            "unit-name":x["params"]["unit-name"],
            "asset-id":x["index"],
            "created-at-round":x["created-at-round"]
         } 
        for x in data["created-assets"]]
    if hash != None:
        assets = [x for x in assets if x["hash"] == hash]
    if fileName != None:
        assets = [x for x in assets if x["name"] == fileName]
    return assets

@app.get("/list_assets")
def list_assets():
    data = indexer_client.account_info(ownerAddress)["account"]
    result =  [
        {
            "name":x["params"]["name"],
            "hash": "null" if "metadata-hash" not in x["params"] else base64.b64decode(x["params"]["metadata-hash"]).hex(),
            "unit-name":x["params"]["unit-name"],
            "asset-id":x["index"],
            "created-at-round":x["created-at-round"]
         } 
        for x in data["created-assets"]]
    return result

@app.get("/get_address")
def get_address():
    return ownerAddress


@app.get("/account_balance")
def get_balance():
    data = indexer_client.account_info(ownerAddress)
    return data["account"]["amount"]