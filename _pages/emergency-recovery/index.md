---
title: Emergency Recovery
---

By default, you sign your `2-of-3` transactions on your `2` hardware wallets (Keystone (formerly Cobo Vault) and Coldcard) that [you previously configured](/setup-wallets/).
If one device is damaged, destroyed or lost, you still have the other good hardware wallet to sign with, and two other seeds to choose from for the second signature: the lost device's [backup seed](/backup-wallet/seeds), and the 3rd seed on your [paper wallet](/setup-wallets/paper).

This page is also useful for testing that you can actually sign a transaction with the paper wallet's seed *before* you deposit significant funds, so you know all 3 seeds work.
It is always a good idea to test your backups.

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

#### Option C - Electrum
Electrum is an open-source software wallet that is free and readily available, but difficult to use with multisig.
**As it will be touching private key material, we strongly recommend you run this on an airgapped machine** (see [advanced section](advanced)).

TODO: add screenshots.

1. Download and install Electrum from [electrum.org](https://electrum.org/).
1. Create a new multisignature wallet using the wizard, and select "2 of 3" as your quorum.
1. Using your Specter-Desktop wallet backup file, identify your `Zpub`s from the JSON or PDF file.
1. For the first two keys (Coldcard and Keystone), import the `Zpub` master public keys into the Electrum multisignature wizard as keys in the multisignature quorum, ensuring the pathway matches the one Specter-Desktop wallet used e.g. `m/48'/0'/0'/2'`.
Electrum will display these as `xpub` master keys.
1. For the seedpicker paper wallet, select private keys, and Electrum will present a box to type in your seedpicker seed.
Ensure you use the drop-down menu to select that this is a BIP39 seed or otherwise Electrum will not correctly recognise and recover this seed.
Notice from this point, you should now consider this private key as 'hot' assuming your Electrum machine is online.
1. You can generate a PSBT (Partially Signed Bitcoin Transaction) from Specter-Desktop, sign it with your remaining good hardware wallet (e.g. the Coldcard or Keystone), and then load that PSBT into Electrum via `Tools` > `Load from file`.
If correctly imported, Electrum will then detect that this transaction has been signed by 1 of 2 required signatures, and present you the opportunity to sign it with the seedpicker paper wallet key. 
1. You can then save this PSBT file and broadcast it via Specter-Desktop. 

The steps above load the paper wallet's seed into Electrum so you can sign with the 3rd key.
Alternatively, import the good hardware wallet's `Zpub` and the *paper wallet's* `Zpub` in step 4, and type in the lost *hardware wallet's* backup seed in step 5.

{% include next_steps.md %}
