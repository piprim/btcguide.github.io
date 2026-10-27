---
title: Blockstream Jade
description: Known issues with the Blockstream Jade, including its blind oracle instead of a secure element, stateless mode and Liquid support.
---

[Jade Plus](https://blockstream.com/jade/) is an inexpensive bitcoin signer with fully open-source hardware and firmware.
It has a camera for QR airgap, can register a multisig wallet and verify its addresses, and works with Specter-Desktop and Sparrow.

#### No Secure Element
Jade stores the seed encrypted with a key that lives on a "blind oracle" server, run by Blockstream by default or by you.
Unlocking with a PIN therefore needs a companion device online, so the device is not airgapped at unlock time, and the oracle is a dependency you must trust to keep running.
Blockstream calls this a "virtual secure element"; the microcontroller itself is not hardened against lab attacks.

#### Stateless Mode
You can avoid the oracle entirely by using Jade as a temporary signer, entering the seed each session by words or a `SeedQR`.
A `SeedQR` is the seed in another encoding: anyone who scans it owns that key, so it must be stored as carefully as the words.
{% include hw/stateless.md %}

#### Also Supports Liquid
Jade is built by Blockstream and supports their Liquid sidechain. Keep it in bitcoin-only mode.

{% include hw/encouragement.md %}
