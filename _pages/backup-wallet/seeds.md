---
title: Backup Seeds
description: Back up each seed phrase on paper, keep them in separate locations with the right companion data, and check them yearly.
---

Remember that anyone who gets access to a quorum of your seeds (`m` in `m-of-n`) as well as your much less secure [public key information](/backup-wallet/public-keys) can steal _all_ of your bitcoin, so **do not store store a quorum of your seeds in one place!**

#### Redundancy
You want to backup each of your 24-word bip39 seed phrases on a piece of paper, so that you can recover if your hardware wallet is lost, defective, or destroyed.
That means at a minimum you'll have 3 pieces of paper, each with 1 seed phrase.
Then, `m` of your seeds along with **all** `n` of your extended public key info (see [Backup Public Keys](/backup-wallet/public-keys)) will allow you to recover your funds.

#### Where to Keep Each Seed
Count every item that can sign as a key: a hardware wallet *and* each seed backup.
In the default `2-of-3` setup that is 5 items: 2 hardware wallets and 3 seed backups (the paper wallet *is* a seed backup).

The rules:

1. **No single location may hold a quorum.** Never keep `m` keys in one place, whether devices, backups or a mix.
A burglar, a fire or a court order should only ever reach one key.
1. **Keep each hardware wallet away from its own backup.** They are the same key, so one location holding both is not a quorum, but one fire would then wipe out that key entirely and leave you one accident from losing everything.
1. **Use at least one metal backup per seed.** Paper fades, burns and smudges; if you must use paper, laminate it and seal it in a bag.
1. **Spread the locations geographically**, so a flood or evacuation in one city cannot take out two keys.
1. **Rotate** if any location is compromised: see [Key Rotation](/key-rotation).

Good locations, roughly from most to least private:

* **A safe at home**, bolted down and fireproof. Hidden and bolted beats expensive.
* **A second spot on your property** that a burglary or fire at the house would not reach (a shed, an outbuilding, under a floor).
* **A safe-deposit box** at a bank or private vault. Fine for *one* key of a multisig, and useful for inheritance since it transfers to your heirs. If you use two boxes, use two different institutions.
* **With a trusted family member or close friend**, who understands they are holding one key of several and must guard it. Give away `m` keys and that person can spend your bitcoin.

Places that are not locations: a drawer, a filing cabinet, a bag, your workplace desk, a photo on your phone, a password manager, "the cloud", or an email draft.
Do not split a single seed across places either; losing one half loses the seed, and multisig already gives you redundancy the right way.

#### What Goes With Each Seed
* A label saying which hardware wallet it belongs to (e.g. `Seed A - Coldcard`).
* A copy of your [public key backup](/backup-wallet/public-keys), so that any `m` locations together hold everything needed to recover.
* Nothing else. No PIN, no passphrase. This guide deliberately uses no passphrase, and a PIN only protects the device; it is not needed for recovery.

#### Check Yearly
Once a year, visit each location, confirm the backup is intact and legible, and confirm the people holding keys still have them and still know what they are.
Every few years, rehearse a recovery [on testnet](/setup-computer/bitcoin-node-advanced#practice-on-testnet).
Put it on your calendar; backups that are never checked rot quietly.


{% include next_steps.md next_url="/backup-wallet/public-keys" next_name="Backup Public Keys" %}
