
Progetto per l'esame di Software Security e Blockchain

# Utilizzo

1. Installare Docker e Docker Compose.
2. Clonare questa repository.
3. Inserire il file `.env` nella directory principale del progetto, assicurarsi che il file sia rinominato in .env .
4. Inserire nel terminale, con permessi di superuser, i seguendi comandi: 
        1. Eseguire lo script `init-prod.sh`.
        2. `docker compose -f compose.yml -f compose-prod.yml up --build`
        3. Accedere all'URL `https://127.0.0.1:8000` attraverso un browser web per interagire con il software.
        4. Il primo utente per ogni ruolo è attivo, si consiglia di creare almeno un utente user, medico e autority.
5. Per terminare l'esecuzione, `docker compose down -v --remove-orphans`.

# Eseguire i test

Per eseguire i test aprire un nuovo terminale con l'applicazione in stato run (l'uso di sudo dipende dal terminale scelto):
1. Eseguire il comando nel terminale per eseguire tutti i test`sudo docker exec app pytest tests/ -v`
2. Per eseguire i singoli test invece usare: `sudo docker exec app pytest tests/test_rate_limit.py -v`
                                             `sudo docker exec app pytest pytest tests/test_autenticazione.py -v`
                                             `sudo docker exec app pytest pytest tests/test_sql_injection.py -v`
                                             `sudo docker exec app pytest pytest tests/test_input_validation.py -v`