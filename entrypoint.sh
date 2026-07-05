#!/bin/sh

echo "In attesa del contract ABI..."
while [ ! -f "/var/artifacts/contracts/$CONTRACT_NAME.sol/$CONTRACT_NAME.json" ]; do
    sleep 2
done

echo "In attesa del contract deployment..."
while [ ! -f "/var/deployments/chain-31337/deployed_addresses.json" ]; do
    sleep 2
done

echo "Creazione tabelle del database..."
python app/init_db.py
exec uvicorn main:app --app-dir app --host 0.0.0.0 --port 8000 --workers $WORKERS

