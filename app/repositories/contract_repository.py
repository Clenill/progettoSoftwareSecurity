
from itertools import starmap
from typing import Any
from app.core.config import w3, W3_ACCOUNT, PRIVATE_KEY
from app.core.exceptions import FunctionNotFoundException, TransactionFailedException
from web3 import Web3
from web3.exceptions import ContractLogicError

class ContractRepository:

    # necessario per capire quale errore specifico è stato generato.
    _error_map = dict(
        starmap(
            lambda name, *args: (
                # Associa l'identificativo dell'errore al suo nome
                '0x' + Web3.keccak(text=f"{name}({','.join(args)})")[:4].hex(), 
                name
            ), 
            [
                ("ZeroDivision", ), 
                ("Unauthorized", ), 
                ("VisitNotFound", "bytes16"), 
                ("DuplicateVisit", "bytes16"), 
                ("LikelihoodNotFound", "uint8"), 
                ("DuplicateLikelihood", "uint8"), 
                ("DuplicateEvidence", "bytes16", "uint8"), 
            ]
        )
    )

    @staticmethod
    def _get_error_name(contract: Any, err: ContractLogicError):
        err_data = getattr(err, "data", "")
        name = ContractRepository._error_map.get(
            err_data[:10] if err_data else "", 
            "UnknownError"
        )
        print("Contract error:", name)
        return name

    @staticmethod
    async def call_function(
        contract: Any, 
        name: str, 
        *args, 
        use_transaction: bool = False
    ):
        try:
            fn = contract.get_function_by_name(name)
        except:
            raise FunctionNotFoundException(name)
        fn = fn(*args) if len(args) else fn()
        if not use_transaction:
            # no transazione, chiama la funzione
            return fn.call({
                "from": W3_ACCOUNT.address
            })

        # transazione
        built_transaction = fn.build_transaction({
            "from": W3_ACCOUNT.address, 
            "nonce": w3.eth.get_transaction_count(W3_ACCOUNT.address), 
            "chainId": w3.eth.chain_id, 
            "gasPrice": w3.eth.gas_price, 
            "gas": 500000
        })

        signed_transaction = w3.eth.account.sign_transaction(
            built_transaction, private_key=PRIVATE_KEY
        )

        transaction_hash = w3.eth.send_raw_transaction(
            signed_transaction.raw_transaction
        )

        transaction_receipt = w3.eth.wait_for_transaction_receipt(
            transaction_hash
        )

        if transaction_receipt["status"] == 0:
            raise TransactionFailedException(transaction_receipt)
        return transaction_receipt

