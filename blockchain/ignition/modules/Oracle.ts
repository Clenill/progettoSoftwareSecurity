import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";
import dotenv from "dotenv";
import path from "path";

dotenv.config({
    path: path.join(
        import.meta.dirname, '..', '..', '..', '.env'
    )
});

if(process.env.W3_ACCOUNT === undefined) {
    console.error("Variabile d'ambiente W3_ACCOUNT invalida: deve essere un indirizzo valido.");
    process.exit(1);
}

if(process.env.SCALE === undefined || isNaN(parseInt(process.env.SCALE))) {
    console.error("Variabile d'ambiente SCALE invalida: deve essere un numero.");
    process.exit(1);
}

if(process.env.INITIAL_PRIOR === undefined || isNaN(parseInt(process.env.INITIAL_PRIOR))) {
    console.error("Variabile d'ambiente INITIAL_PRIOR invalida: deve essere un numero.");
}

export default buildModule("OracleModule", (m) => {
    const account = process.env.W3_ACCOUNT || '';
    const scale = parseInt(process.env.SCALE || '100000000');
    const initialPrior = parseFloat(process.env.INITIAL_PRIOR || '0.5');
    const oracle = m.contract("Oracle", [account, scale, initialPrior * scale]);

  return { oracle };
});
