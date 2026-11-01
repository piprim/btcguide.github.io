---
title: Common Hardware Wallet Issues
description: Shortcomings shared by several hardware wallets, explained once: closed source, slow PSBT adoption, shared Python code, altcoins, stateless designs, U2F, drivers and USB.
---

Several hardware wallets share the same shortcomings.
Each device page in this guide names the ones that apply to it and links here for the full explanation.

## Closed Source
While some code may be open source, it is impossible for end-users to verify how their software actually works, and thus they must instead rely on trust.
This is usually because a device uses a so-called Secure Element whose manufacturer requires its code to be kept closed-source and under NDA.
This process of "security through obscurity" is generally considered a [bad](https://stackoverflow.com/questions/533965/why-is-security-through-obscurity-a-bad-idea) [practice](https://en.wikipedia.org/wiki/Security_through_obscurity) in the information security community.
Vendors do reveal their code to others under NDA and publish the results of third party audits of their code.

The popular bitcoin ethos of "don't trust, verify" is incompatible with software that isn't 100% open-source.

## Limited BIP174 (PSBT) Support
Partially Signed Bitcoin Transactions (PSBT or [BIP174](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki)) was proposed in July 2017 and merged into Bitcoin Core [in October 2018](https://bitcoin.org/en/release/v0.17.0#bip-174-partially-signed-bitcoin-transactions-support).
Wallets that don't update their software could easily become abandonware.

## Written in Python
This is not inherently a problem (python is a good general-purpose programming language!), but several hardware wallets with varying level of multisig support are written in python, including: Trezor, Coldcard, KeepKey, Specter-DIY, and Passport.
These hardware wallets share *a lot* of upstream code, and it's possible that if a vulnerability were discovered in one it would be present in the others.

## Altcoin-Focused
In theory, supporting altcoins does not fundamentally weaken bitcoin security.
In practice, the more complex a codebase is the more likely a security bug will be introduced (or go undetected).
These wallets are liable to be slow to upgrade their security, and [bit rot](https://en.wikipedia.org/wiki/Software_rot) is more likely to set in.

## Stateless Wallets are Not Well-Suited for Multisig
To get the benefits of multisig without taking on new risks, you must [verify a receive address](/known-issues/verify-receive-address) before use.
Stateless wallets can only verify that this hardware controls `1` of your `m` (as in `m-of-n`) keys.
You can read more about this attack and potential mitigations [here](/known-issues/verify-receive-address).
While stateful wallets do not 100% eliminate this attack vector, they provide an extra layer of security where it is needed most.

## Alternate Use: U2F Key
Some wallets can be converted to a [Universal 2nd Factor (U2F)](https://en.wikipedia.org/wiki/Universal_2nd_Factor) key for logging into trusted third parties like Twitter, Google, Facebook, LinkedIn, DropBox, etc.
While this won't have any direct impact on the security of bitcoin private keys that are under your physical control, it does significantly impair hackers' ability to wreak havoc on your digital life.

*If you use a wallet as a U2F key, you should probably use it only for that purpose and not for storing bitcoin*.
There are already many reputable U2F hardware providers and their dedicated products are very affordable, so it is *not* recommended to buy a hardware wallet for use as a U2F key.
However, U2F keys can be a good way to make use of a retired bitcoin hardware wallet.

## Complex Driver Configuration
In order to connect a hardware wallet to your computer (thus breaking the "airgap"), your computer needs to be configured to interact with it.
Advanced users will need to setup [udev rules](https://github.com/spesmilo/electrum/tree/master/contrib/udev).

## Wired "Airgap"
Some devices must be connected to your computer in order to function.
Wired connections are bad because the USB stack presents massive attack vectors; the whole point of hardware wallets is to keep your keys offline.
