---
title: Emergency Recovery
---

By default, you sign your `2-of-3` transactions on your `2` hardware wallets (Keystone (formerly Cobo Vault) and Coldcard) that [you previously configured](/setup-wallets/).
If one device is damaged, destroyed or lost, you still have the other good hardware wallet to sign with, and two other seeds to choose from for the second signature: the lost device's [backup seed](/backup-wallet/seeds), and the 3rd seed on your [paper wallet](/setup-wallets/paper).

This page is also useful for testing that you can actually sign a transaction with the paper wallet's seed *before* you deposit significant funds, so you know all 3 seeds work.
It is always a good idea to test your backups, and you can rehearse the whole procedure [on testnet](/setup-computer/bitcoin-node-advanced#practice-on-testnet) first.

You have several options.

#### Option A - Replace the hardware wallet
Replace the damaged device with a new one and load it with the same seed phrase that [you previously backed up](/backup-wallet/seeds).
This means that if seed phrase A was on your Keystone and your Keystone was destroyed in a fire, you would do the following:

1. Buy a new Keystone.
1. Find the backup of seed phrase A that [you previously made](/backup-wallet/seeds).
1. Load seed phrase A onto your new (replacement) Keystone.
1. Follow [the previous hardware wallet setup steps](/setup-wallets/) to add the new device into your multisig.

However, if for any reason that doesn't work (perhaps devices are sold out or the company has gone out of business), you can load a BIP39 seed onto another device.
For this, we have two recommendations: Trezor (hardware wallet) and Electrum (software wallet).
Both have tradeoffs, and we hope that there will be better options in the future.
BIP39 is the gold standard supported by all major hardware wallets, so we expect it will continue to be compatible with new hardware wallets as they are developed in the future.

As there are "gotchas" in both of the below setups, we recommend you read [the advanced section](advanced) for tips to improve your setup.

#### Option B - Trezor
You should be aware that this is a little more complicated than hardware wallets you setup previously, and there are some pitfalls to avoid (see [known issues](/known-issues/hardware/trezor)).

On the Trezor you can load either the lost hardware wallet's backup seed, or the 3rd seed from your paper wallet.
(You could also load the paper wallet's seed into the replacement device in Option A, but keeping each device paired with its original seed avoids confusing yourself in Specter-Desktop.)

TODO: add explanation/screenshots.

#### Option C - Sparrow (software wallet)
[Sparrow](https://sparrowwallet.com/) is a free, open-source desktop wallet with first-class multisig support.
It replaces the Electrum instructions that used to be here, which broke on importing cosigner keys.
**As it will be touching private key material, run it on an airgapped machine** (see [advanced section](advanced)).

TODO: add screenshots.

1. Download Sparrow from [its download page](https://sparrowwallet.com/download/), verify the signature, and install it on your airgapped machine.
1. Have your [public key backup](/backup-wallet/public-keys) at hand: you need the fingerprint, derivation path and `Zpub` of all 3 keys.
1. `File` > `New Wallet`, name it, set `Policy Type` to `Multi Signature`, leave `Native Segwit` and `2 of 3`.
1. Fill in the 3 keystores:
   * For each key you are **not** signing with, choose `xPub / Watch Only Wallet` and type its fingerprint, derivation path (`m/48'/0'/0'/2'`) and `Zpub` from the backup.
   Airgapped devices can also be imported with `Airgapped Hardware Wallet` from their export file or QR code.
   * For the key you **are** signing with (normally the paper wallet seed), choose `New or Imported Software Wallet` > `Mnemonic Words (BIP39)` > `Enter 24 Words`, type the words, leave the passphrase empty, and wait for `Valid checksum`.
   Click `Create Keystore`, check the derivation path reads `m/48'/0'/0'/2'`, then `Import Keystore`.
   From this moment that seed is "hot" on this machine.
1. **Before anything else**, compare the fingerprint and `Zpub` Sparrow now shows for that keystore with your public key backup.
If they differ, you typed a word wrong or the derivation path is off; fix it before continuing.
1. Click `Apply`. Sparrow's first receive address must match the one Specter-Desktop shows for the same index; if it does, the wallet is rebuilt correctly.
1. In Specter-Desktop, create the transaction, sign it with your remaining good hardware wallet, and save the PSBT (Partially Signed Bitcoin Transaction) to a file or show it as a QR code.
1. In Sparrow: `File` > `Open Transaction` (or `Load PSBT` from file, or `Scan QR`), check the destination and amount, click `Sign`, then `Save PSBT` or `Show QR`.
1. Load the signed PSBT back into Specter-Desktop and broadcast it.
1. Afterwards, wipe the airgapped machine and [rotate](/key-rotation) the key you typed in if the machine was ever less than fully trusted.

The steps above type the paper wallet's seed into Sparrow so you can sign with the 3rd key.
Alternatively, enter the good hardware wallet's and the *paper wallet's* keys as watch-only, and type the lost *hardware wallet's* backup seed as the software keystore.

If a seed may have been exposed rather than just lost, don't stop at recovery: [rotate the key](/key-rotation).

{% include next_steps.md next_url="/key-rotation" next_name="Key Rotation" %}
