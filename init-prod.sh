#!/bin/sh

W3_ACCOUNT="$1"

if [ -z "$W3_ACCOUNT" ]; then
    printf "Indirizzo dell'account da utilizzare per le operazioni: "
    read W3_ACCOUNT
fi

rm -rf blockchain/config/networkFiles
sed "s/W3_ACCOUNT/${W3_ACCOUNT}/g" blockchain/config/qbftConfigFile.template.json > blockchain/config/qbftConfigFile.json

echo "Generazione della configurazione dei nodi della rete..."
docker run --rm -u $SUDO_UID:$SUDO_GID -v "$(pwd)/blockchain/config:/data" hyperledger/besu:26.6.1 operator generate-blockchain-config --config-file=/data/qbftConfigFile.json --to=/data/networkFiles

for i in $(seq 1 4); do
    NODE_ADDR=$(ls -d blockchain/config/networkFiles/keys/*/ | head -n 1)
    sed -i "s/^0x//" "$NODE_ADDR/key.priv"
    sed -i "s/^0x//" "$NODE_ADDR/key.pub"
    mv $NODE_ADDR "$(pwd)/blockchain/config/networkFiles/keys/node$i"
done

NODE_1_IPV4="172.20.0.11"
PUBLIC_KEY=$(cat blockchain/config/networkFiles/keys/node1/key.pub | tr -d '\n' | tr -d '\r')
ENODE="enode://${PUBLIC_KEY}@${NODE_1_IPV4}:30303"
echo "Indirizzo enode del primo nodo: $ENODE"

sed "s|\${ENODE}|$ENODE|g" compose-prod.template.yml > compose-prod.yml
echo "Configurazione terminata!"

