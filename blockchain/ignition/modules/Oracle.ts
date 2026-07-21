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

export default buildModule("OracleModule", (m) => {
  const oracle = m.contract("Oracle", [process.env.W3_ACCOUNT, process.env.SCALE]);

  return { oracle };
});
