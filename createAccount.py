from algosdk import account, mnemonic
import json
privatekey,address = account.generate_account()
phrase = mnemonic.from_private_key(privatekey)
data={
    "address":address,
    "mnemonic":phrase
}
print("-----")
print(json.dumps(data, indent=2))
print("-----")