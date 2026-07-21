#!/bin/sh

echo "In attesa del contract ABI..."
while [ ! -f "/var/artifacts/contracts/$CONTRACT_NAME.sol/$CONTRACT_NAME.json" ]; do
    sleep 2
done

echo "In attesa del contract deployment..."
while [ ! -f "/var/deployments/chain-$NETWORK_ID/deployed_addresses.json" ]; do
    sleep 2
done

if [ ! -f /etc/ssl/cert.pem ] || [ ! -f /etc/ssl/key.pem ]; then
    echo "Certificato non trovato. Generazione di un nuovo certificato..."
    openssl req \
        -x509 \
        -nodes \
        -days 365 \
        -newkey rsa:4096 \
        -keyout /etc/ssl/key.pem \
        -out /etc/ssl/cert.pem \
        -config /usr/backend/localhost.cnf
    chown -R ${USER_ID}:${GROUP_ID} /etc/ssl
fi

echo "Creazione tabelle del database..."
python app/init_db.py
echo "Avvio di uvicorn..."
exec uvicorn main:app --app-dir app --host 0.0.0.0 --port 8000 --ssl-keyfile /etc/ssl/key.pem --ssl-certfile /etc/ssl/cert.pem

