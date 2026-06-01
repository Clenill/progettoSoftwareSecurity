import { buildModule } from "@nomicfoundation/hardhat-ignition/modules";

export default buildModule("OracleModule", (m) => {
  const oracle = m.contract("Oracle");

  // call constructor...

  return { oracle };
});
