# Chainlink wallet & keystore import (DO NOT COMMIT KEYS)

This document explains how to create a keystore for the Chainlink node and securely provide it to the container.

## Create a keystore (geth example)
1. Install geth on a secure machine (not the repo):
   sudo apt-get install -y software-properties-common
   sudo add-apt-repository -y ppa:ethereum/ethereum
   sudo apt-get update
   sudo apt-get install -y golang-geth

2. Create a new account and keystore:
   mkdir -p ~/chainlink-keystore
   geth account new --datadir ~/chainlink-keystore
   # follow prompts and choose a strong passphrase

3. Copy the keystore file into the project folder (on the host only):
   mkdir -p ./chainlink/keystore
   cp ~/chainlink-keystore/keystore/* ./chainlink/keystore/
   chmod 600 ./chainlink/keystore/*

## Importing keystore to Chainlink node
- The Chainlink container mounts ./chainlink as /chainlink. Place your keystore JSON under ./chainlink/keystore/.
- Do NOT commit the keystore or private keys to git. Use host file permissions or a secret manager.

## Funding the wallet
- Use a testnet faucet for test networks (Goerli, Sepolia, etc.) or transfer ETH to the keystore address for mainnet.
- Verify the address and balance using an explorer or web3 tools.

## Notes
- Alternatively you can create an encrypted JSON keystore via ethers.js or other wallet tooling and place it in the same keystore directory.
- Chainlink may also support importing keys via its CLI or UI depending on node version; consult Chainlink docs for exact steps.

---
