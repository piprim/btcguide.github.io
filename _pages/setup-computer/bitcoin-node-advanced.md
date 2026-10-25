---
title: Configure Bitcoin Node
---

## Verify Software

#### Simple: Verify Signature
Bitcoin Core developer Luke Dashjr has a good guide titled [How to securely install Bitcoin](https://medium.com/@lukedashjr/how-to-securely-install-bitcoin-9bfeca7d3b2a). It explains and steps through the process of ensuring your install of Bitcoin is secure and free of malware.

#### Complicated: Build from Source
TODO: add link

## Run Node Over Tor
Jameson Lopp has a good guide on increasing the privacy of your node (as well as the Bitcoin network in general) by running your node over Tor:

[https://blog.lopp.net/how-to-run-bitcoin-as-a-tor-hidden-service-on-ubuntu/](https://blog.lopp.net/how-to-run-bitcoin-as-a-tor-hidden-service-on-ubuntu/)

## Practice on Testnet
Testnet is a copy of the bitcoin network whose coins are worthless, so you can run through this entire guide (including [emergency recovery](/emergency-recovery)) without risking funds.
We strongly recommend a full dry run on testnet before moving real bitcoin.

1. Add `testnet=1` to your `bitcoin.conf` and restart Bitcoin Core.
It syncs the much smaller testnet chain into a separate `testnet3` folder; your mainnet data is untouched.
1. Specter-Desktop follows whatever network your node is on, so once it reconnects it shows testnet (addresses start with `tb1`).
1. Switch each hardware wallet to testnet.
On Coldcard this is deliberately buried: `Settings` > `Danger Zone` > `Testnet Mode` (older firmware: `Advanced` > `Danger Zone`).
On Keystone, testnet needs the Bitcoin-only firmware; look for the testnet option in its Bitcoin settings.
1. Generate a fresh practice seed on each device and in seedpicker (pick `Testnet` in its export box) rather than reusing your real seeds, so no real seed is ever typed into a device in an unusual mode.
1. Get coins from a testnet faucet (search for "bitcoin testnet faucet"), then practice receiving, verifying addresses, sending, and recovering with the 3rd key.
1. When done, remove `testnet=1`, restart Bitcoin Core, switch the devices back to mainnet, and start the guide for real with new seeds.

## Guide to Deploying Node on AWS:
[https://wolfmcnally.com/115/developer-notes-setting-up-a-bitcoin-node-on-aws/](https://wolfmcnally.com/115/developer-notes-setting-up-a-bitcoin-node-on-aws/)


{% include next_steps.md next_url="/setup-computer/specter" next_name="Install Specter-Desktop" %}
