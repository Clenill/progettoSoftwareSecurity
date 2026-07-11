import hardhatToolboxMochaEthersPlugin from "@nomicfoundation/hardhat-toolbox-mocha-ethers";
import { configVariable, defineConfig } from "hardhat/config";
import dotenv from "dotenv";
import path from "path";

dotenv.config({
    path: path.join(import.meta.dirname, '..', '.env')
});

export default defineConfig({
  plugins: [hardhatToolboxMochaEthersPlugin],
  solidity: {
    profiles: {
      default: {
        version: "0.8.28",
      },
      production: {
        version: "0.8.28",
        settings: {
          optimizer: {
            enabled: true,
            runs: 200,
          },
        },
      },
    },
  },
  networks: {
    hardhatMainnet: {
      type: "edr-simulated",
      chainType: "l1",
    },
    hardhatOp: {
      type: "edr-simulated",
      chainType: "op",
    },
    sepolia: {
      type: "http",
      chainType: "l1",
      url: configVariable("SEPOLIA_RPC_URL"),
      accounts: [configVariable("SEPOLIA_PRIVATE_KEY")],
    },
    besu_prod: {
      type: "http", 
      chainId: parseInt(process.env.NETWORK_ID || '1337'), 
      url: process.env.RPC_URL || 'http://127.0.0.1:8545', 
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [], 
      gas: 6000000, 
      gasPrice: 0
    }
  },
});
