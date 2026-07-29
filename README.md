
Progetto per l'esame di Software Security e Blockchain

# Utilizzo

1. Installare Docker e Docker Compose.
2. Clonare questa repository.
3. Inserire il file `.env` nella directory principale del progetto, assicurarsi che il file sia rinominato in .env .
4. (Opzionale) Inserire certificato e chiave privata da utilizzare nella directory `ssl`
5. Inserire nel terminale, con permessi di superuser, i seguendi comandi:
    - Se si vuole eseguire la versione di test del progetto:
        1. `docker compose -f compose.yml -f compose-dev.yml up` ed accedere all'URL `https://127.0.0.1:<porta app scelta>` attraverso un browser web per interagire con il software. 
    - Se si vuole eseguire la versione di produzione del progetto, che utilizza Hyperledger Besu:
        1. Eseguire lo script `init-prod.sh`.
        2. `docker compose -f compose.yml -f compose-prod.yml up`
        3. Accedere all'URL `https://127.0.0.1:<porta app scelta>` attraverso un browser web per interagire con il software.
6. Per terminare l'esecuzione, `docker compose down -v --remove-orphans`.

# Eseguire i test

Per eseguire i test (l'uso di sudo dipende dal terminale scelto):
1. Eseguire il comando nel terminale per eseguire tutti i test`sudo docker exec app pytest tests/ -v`
2. Per eseguire i singoli test invece usare: sudo docker exec app pytest tests/test_rate_limit.py -v
                                             sudo docker exec app pytest pytest tests/test_autenticazione.py -v
                                             sudo docker exec app pytest pytest tests/test_sql_injection.py -v
                                             sudo docker exec app pytest pytest tests/test_input_validation.py -v
