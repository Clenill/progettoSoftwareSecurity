
Progetto per l'esame di Software Security e Blockchain

# Utilizzo

1. Installare Docker e Docker Compose.
2. Clonare questa repository.
3. Creare e modificare il file `.env` partendo dal file `.env.example` presente nella repository, inserendo i valori desiderati per la configurazione.
4. Inserire nel terminale, con permessi di superuser, i seguendi comandi:
    - Se si vuole eseguire la versione di test del progetto:
    1. `docker compose -f compose.yml -f compose-dev.yml up` ed accedere all'URL `http://127.0.0.1:<porta app scelta>` attraverso un browser web per interagire con il software. 
    - Se si vuole eseguire la versione di produzione del progetto, che utilizza Hyperledger Besu:
    1. Eseguire lo script `init-prod.sh` inserendo come parametro (oppure quando richiesto, in fase di esecuzione) l'indirizzo dell'account Web3 da utilizzare per le operazioni della blockchain.
    2. `docker compose -f compose.yml -f compose-prod.yml up`
    3. Posizionarsi all'interno della directory `blockchain` ed eseguire `npx hardhat ignition deploy ignition/modules/Oracle.ts --network besu_prod` per effettuare il deployment dello smart contract.
    4. Accedere all'URL `http://127.0.0.1:<porta app scelta>` attraverso un browser web per interagire con il software.
5. Per terminare l'esecuzione, `docker compose down`.

# Eseguire i test

Per eseguire i test (nella directory `/tests`):
1. Installare `pytest`, `pytest-asyncio` e `httpx` con `pip install pytest pytest-asyncio httpx`
2. Eseguire il comando `pytest tests/<nome test>.py -v`

