
import { network } from "hardhat";
import fs from "fs";
import path from "path";

async function main(): Promise<void> {
    const connection = await network.create();
    const { ethers } = connection;
    const signers = await ethers.getSigners();
    const deployer = signers[0];
    if(!deployer) {
        throw new Error("Nessun account di deployment trovato.");
    }

    const balance: bigint = await ethers.provider.getBalance(deployer.address);
    if(balance === 0n) {
        throw new Error("L'account di deployment non ha fondi");
    }

    console.log("Tentativo di deployment con parametri:");
    console.log(`CONTRACT_NAME: ${process.env.CONTRACT_NAME}`);
    console.log(`W3_ACCOUNT: ${process.env.W3_ACCOUNT}\nSCALE: ${process.env.SCALE}\nNETWORK_ID: ${process.env.NETWORK_ID}`);

    const account = process.env.W3_ACCOUNT || '';
    const scale = parseInt(process.env.SCALE || '100000000');
    const initialPrior = parseFloat(process.env.INITIAL_PRIOR || '0.5');
    const initialTrueLikelihood = parseFloat(process.env.INITIAL_TRUE_LIKELIHOOD || '0.5');
    const initialFalseLikelihood = parseFloat(process.env.INITIAL_FALSE_LIKELIHOOD || '0.5');

    console.log('INITIAL PRIOR: ', initialPrior * scale);
    console.log('INITIAL TRUE LIKELIHOOD: ', initialTrueLikelihood * scale);
    console.log('INITIAL FALSE LIKELIHOOD: ', initialFalseLikelihood * scale);

    const factory = await ethers.getContractFactory(process.env.CONTRACT_NAME);
    const contract = await factory.deploy(
        account, 
        scale, 
        initialPrior * scale, 
        initialTrueLikelihood * scale, initialFalseLikelihood * scale, {
            gasPrice: 0n, 
            gasLimit: 5000000n
        }
    );

    console.log("In attesa della conferma dal nodo...");
    await contract.waitForDeployment();
    const address: string = await contract.getAddress();
    console.log("Deployment concluso! Indirizzo:", address);
    const key = `${process.env.CONTRACT_NAME}Module#${process.env.CONTRACT_NAME}`;

    const outputData = {
        [key]: address
    };
    const outputPath = `/usr/blockchain/ignition/deployments/chain-${process.env.NETWORK_ID}`;

    fs.mkdirSync(outputPath, { recursive: true });
    fs.writeFileSync(path.join(outputPath, 'deployed_addresses.json'), JSON.stringify(outputData, null, 2), 'utf-8');
}

main()
    .then(() => process.exit(0))
    .catch((err: Error) => {
        console.error("Errore:", err);
        process.exit(1);
    });


