---
title: SeedSigner
description: SeedSigner is a stateless DIY QR signer. The trade-offs are building it yourself, no physical security, and entering the seed every session.
---

[SeedSigner](https://seedsigner.com/) is a stateless signing device you build yourself from a Raspberry Pi Zero, a camera and a small screen for around $50.
It is fully open source, communicates only by QR code, and supports native segwit multisig key export and PSBT signing with Specter-Desktop and Sparrow.
Because it never stores a seed, it is also a good upgrade from this guide's [paper wallet](/setup-wallets/paper): you keep the seed on paper (or as a `SeedQR`) and only load it when signing.

#### Must Be Built
It is a kit, not a product. Parts come from ordinary electronics shops, which makes supply-chain tampering less targeted, but assembly and flashing are on you.

#### No Physical Security
There is no secure element and no PIN: whoever holds your seed backup holds the key.
This is the same trade-off as a metal seed plate, which is what the paper wallet already accepts.

#### Seed Entered Every Session
Typing 24 words each time is tedious; a `SeedQR` printed from the device makes it quick, but is an unencrypted copy of the seed and must be stored as one.

{% include hw/stateless.md %}
SeedSigner can load your multisig descriptor by QR each session to verify addresses, which mitigates this as long as you actually do it.

{% include hw/encouragement.md %}
