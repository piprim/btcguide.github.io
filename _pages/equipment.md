---
title: Equipment
description: The hardware wallets, computer and Bitcoin Core node you need for a 2-of-3 multisig, with advice on choosing the second hardware wallet.
---

TODO: add diagram showing how all these pieces interact.

This guide will assume your computer is running the free and open source [Ubuntu](https://ubuntu.com/) operating system, because it offers a good mix of security, bitcoin software compatibility, and end-user configurability.
Advanced users should be able to get other operating systems to work, but you will be on your own to figure that out for now.

The purpose of the computer will be to run [Specter-Desktop](https://github.com/cryptoadvance/specter-desktop), which will communicate blockchain information between [Bitcoin Core](https://bitcoin.org/en/full-node) and your hardware wallets for verification and signing.
You will need an up-to-date Bitcoin Core Full Node, which can be running on this same computer or another.
For more information about this, see [Configure Bitcoin Node](/setup-computer/bitcoin-node).
Bitcoin Core's initial block download takes a few days to sync, so we recommend you get started on that while you wait for your hardware wallets to arrive.

#### Minimum Equipment to Buy:

* 1 low-end computer with webcam - see below for more information about system requirements
* 1 [Keystone](https://keyst.one/) hardware wallet (Essential or Pro model)
* 1 [Coldcard](https://coldcard.com/) with 1 microSD card, **or** another device from a different vendor than your Keystone - see [Choosing the Second Hardware Wallet](#choosing-the-second-hardware-wallet) below
* 1 DVD-R (if your computer has a DVD drive) or USB stick for installing [Ubuntu](https://ubuntu.com/)
* 1 pen + 3 pieces of paper (or notecards) to write down your BIP39 seed phrases
* 1 printer, 2 pieces of paper, and scissors - to print out [2 pages](setup-wallets/paper#generate-seed) of non-sensitive (public) information. You don't need to buy a printer if you can ask someone else to print these pages out for you. You will use the scissors to cut out the words.

#### Choosing the Second Hardware Wallet
The step-by-step pages in this guide use a [Coldcard](/setup-wallets/coldcard).
It is still an acceptable choice, but only with precautions: a firmware bug made Coldcard-generated seeds guessable from 2021 to 2026, and the vendor was slow to disclose it (see [known issues](/known-issues/hardware/coldcard)).
If you use one:

* Update the firmware **before** generating any seed.
* Generate the seed from 50 or more of your own dice rolls (see [advanced setup](/setup-wallets/coldcard-advanced)), so you never depend on the device's random number generator.
* Keep it as one key among devices from different vendors, as this guide does; Coldcard owners who did so lost nothing in 2026.

Any other device works with the same steps if it meets these requirements:

* Supports PSBTs (Partially Signed Bitcoin Transactions) and native segwit multisig, and can *register* the multisig wallet on the device so it can verify receive addresses.
* Communicates by QR code or microSD card rather than USB, to keep the airgap.
* Open-source firmware.
* Made by a different vendor than your other hardware wallet, so one vendor's bug cannot cost you two keys.

Devices that meet them today, with their trade-offs:

| Device | Airgap | Notes |
|--------|--------|-------|
| [Coldcard](/known-issues/hardware/coldcard) | microSD (Q model also QR) | Secure element, best multisig tooling; use dice for the seed and weigh the vendor's 2026 track record |
| [Passport Prime](/known-issues/hardware/passport) | QR + microSD, but has Bluetooth and NFC radios | Secure element, polished, expensive; the airgapped Passport Core was discontinued in 2026 |
| [Jade Plus](/known-issues/hardware/jade) | QR + microSD | Cheap; no secure element, unlock relies on an online "oracle" unless used stateless |
| [SeedSigner](/known-issues/hardware/seedsigner) | QR only | Build it yourself from a Raspberry Pi; stateless; also a good upgrade from the paper wallet |
| [BitBox02](/known-issues/hardware/bitbox) | None (USB) | Solid device, but breaks this guide's airgap rule |

Whichever you choose, any microSD card must be 32 GB or smaller for `FAT` formatting; much smaller is fine.

#### Computer System Requirements
The software you're running on this machine has very low resource requirements, so you can likely repurpose an old laptop that you have laying around.
You can read the exact Ubuntu Desktop System requirements [here](https://help.ubuntu.com/community/Installation/SystemRequirements).
Most notably, you'll want the machine to be 64-bit, have at least 4GB RAM, and a 2 GHz dual-core processor.

While the optimal laptop would not be used for anything else, it is acceptable for this to be a multi-purpose machine that you use day-to-day; by design this laptop will not see bitcoin private key material and we will always treat it as-if it is infected by malware.

You do not need to use a laptop, any desktop computer can work. We find laptops ideal because:

* They are portable and have batteries, meaning they can easily be taken into secure rooms (like bank vaults) that may not have a power source.
* They usually have built-in webcams, which are needed for a high-quality [airgap](https://en.wikipedia.org/wiki/Air_gap_(networking)) (using QR codes) that we will be using. It's also easy to physically pick up laptops to scan QR codes if needed.
* They have less cables for the mouse/keyboard, which is helpful when dealing with the clutter of multiple hardware wallets.

## Bitcoin Core Node
For regular users, we recommend using
[RaspiBlitz](https://shop.fulmo.org/raspiblitz/),
[MyNode](https://mynodebtc.com/), 
[Nodl](https://www.nodl.it/), or
[Umbrel](https://www.umbrel.io/)

(more [here](/setup-computer/)).

For advanced users, you can [run your own Bitcoin Core node](setup-computer/bitcoin-node) for more details.


{% include next_steps.md next_url="/setup-computer" next_name="Configure Your Computer" %}
