#!/bin/sh

set -e
USER_ID=$(id -u "$(logname)")
GROUP_ID=$(id -g "$(logname)")
NETWORK_ID=$(cat .env | grep NETWORK_ID | grep -E -o [0-9]+)
W3_ACCOUNT=$(cat .env | grep W3_ACCOUNT | grep -E -o "=.*" | grep -E -o "[a-zA-Z0-9]+")


echo "Rimozione della vecchia configurazione..."
rm -rf blockchain/config/networkFiles

echo "Generazione della configurazione dei nodi della rete..."
sed "s/W3_ACCOUNT/${W3_ACCOUNT}/g" blockchain/config/qbftConfigFile.template.json > blockchain/config/qbftConfigFile.json
docker run --rm -u "$USER_ID:$GROUP_ID" -v "$(pwd)/blockchain/config:/data" hyperledger/besu:26.6.1 operator generate-blockchain-config --config-file=/data/qbftConfigFile.json --to=/data/networkFiles

for i in $(seq 1 4); do
    NODE_DIR=$(ls -d blockchain/config/networkFiles/keys/*/ | head -n 1)
    sed -i "s/^0x//" "$NODE_DIR/key.priv"
    sed -i "s/^0x//" "$NODE_DIR/key.pub"
    mv "$NODE_DIR" "$(pwd)/blockchain/config/networkFiles/keys/node$i"
done

echo "Configurazione degli indirizzi enode dei nodi..."
NODE_1_IPV4="172.20.0.11"
PUBLIC_KEY=$(cat blockchain/config/networkFiles/keys/node1/key.pub | tr -d '\n' | tr -d '\r')
ENODE="enode://${PUBLIC_KEY}@${NODE_1_IPV4}:30303"
echo "Indirizzo enode del primo nodo: $ENODE"
sed "s|\${ENODE}|$ENODE|g" compose-prod.template.yml > compose-prod.yml

echo "Configurazione delle directory e dei permessi..."
mkdir -p blockchain/artifacts
mkdir -p blockchain/ignition/deployments/chain-"${NETWORK_ID}"
mkdir -p logs
mkdir -p ssl/certs
mkdir -p ssl/private
chown -R "$USER_ID:$GROUP_ID" compose-prod.yml blockchain/ logs/ ssl/

if ! grep -q "^\s*USER_ID" .env; then
    echo -e "\nUSER_ID=$USER_ID" >> .env
fi
if ! grep -q "^\s*GROUP_ID" .env; then
    echo "GROUP_ID=$GROUP_ID" >> .env
fi

echo "Configurazione terminata!"

