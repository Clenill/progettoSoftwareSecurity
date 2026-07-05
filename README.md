
Progetto per l'esame di Software Security e Blockchain

# Utilizzo

1. Installare Docker e Docker Compose.
2. Creare il file `.env` partendo dal file `.env.example` presente nella repository.
3. Eseguire `docker compose -f compose.yml -f compose-<ambiente>.yml up --build` nel terminale con permessi di superuser per avviare l'esecuzione, dove `<ambiente>` è `dev` o `prod`.
4. Accedere all'indirizzo `http://127.0.0.1:<porta>` attraverso un browser web per interagire con il software, dove `<porta>` è la porta specificata nelle variabili d'ambiente `.env`.
5. Eseguire `docker compose down` nel terminale con permessi di superuser per fermare l'esecuzione.

