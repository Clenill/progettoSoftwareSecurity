
from typing import Any
from app.core.config import w3, W3_ACCOUNT, PRIVATE_KEY

class ContractService:
    @staticmethod
    async def call_function(contract: Any, name: str, *args, use_transaction=False):
        try:
            fn = contract.get_function_by_name(name)
        except:
            raise ValueError("Funzione non trovata nel contratto")
        if not use_transaction:
            if len(args):
                return fn(*args).call()
            else:
                return fn().call()
        tx_build = fn(*args).build_transaction({
            "from": W3_ACCOUNT.address, 
            "nonce": w3.eth.get_transaction_count(W3_ACCOUNT.address), 
            "chainId": w3.eth.chain_id, 
            "gasPrice": w3.eth.gas_price, 
            "gas": 500000
        })
        tx_signed = w3.eth.account.sign_transaction(
            tx_build, private_key=PRIVATE_KEY
        )
        tx_hash = w3.eth.send_raw_transaction(tx_signed.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if tx_receipt['status'] == 0:
            raise RuntimeError("Transazione fallita")
        return tx_receipt

