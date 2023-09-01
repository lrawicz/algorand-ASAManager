from typing import Union
from typing_extensions import Annotated
from fastapi import FastAPI,HTTPException, Header
from pydantic import BaseModel

from algosdk.v2client import algod,indexer
import algosdk
import re
import json
import base64



with open("config.json", "r") as config_file:
    config = json.load(config_file)
ownerPrivKey = algosdk.mnemonic.to_private_key(config["mnemonic"])
ownerAddress = algosdk.account.address_from_private_key(ownerPrivKey)
network = config["network"]["value"]
algod_client = algod.AlgodClient(config["network"]["apiToken"], config["network"][network]["node"])
indexer_client = indexer.IndexerClient(config["network"]["apiToken"], config["network"][network]["indexer"])

app = FastAPI()

@app.get("/")
def index():
    
    return ({
        "appName":config['appName'],
        "version":config['version']
    })

class asset(BaseModel):
    fileName: str
    hashString: str

@app.post("/create_asset")
def create_asset(asset:asset,x_token: Annotated[Union[str, None], Header()] = None):
    if config["x-token"] != x_token:
        raise HTTPException(status_code=401, detail="Invalid x-token. Anauthorized.")
    if (re.search("[^a-f0-9]",asset.hashString) != None or
        not re.compile(r'^[0-9a-fA-F]{64}$').match(asset.hashString)):
        raise HTTPException(status_code=422, detail="invalid hash data")
    hashBytes = bytes.fromhex(asset.hashString)
    
    unsigned_tx = algosdk.transaction.AssetCreateTxn(
        sender=ownerAddress,
        sp = algod_client.suggested_params(),
        total= 1,
        decimals= 0,
        default_frozen=True,
        manager=ownerAddress,
        reserve=ownerAddress,
        freeze=ownerAddress,
        clawback=ownerAddress,
        metadata_hash= hashBytes,
        unit_name="PDF_HASH",
        asset_name=asset.fileName
    )
    signed_tx = unsigned_tx.sign(ownerPrivKey)
    
    tx_id = algod_client.send_transaction(signed_tx)
    result ={
        "tx_id": tx_id
    }
    return result

@app.get("/find_asset")
async def find_asset(fileName: Union[str,None] = None,hash: Union[str,None] = None):
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