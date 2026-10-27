---
title: BitBox02
description: The BitBox02 is a solid multisig signer, but with USB only and a closed secure chip firmware it is not on the recommended list.
---

The [BitBox02](https://bitbox.swiss/) Bitcoin-only edition has a secure element, open-source firmware, and good multisig support including on-device registration of the cosigners.
It works with Specter-Desktop and Sparrow.

{% include hw/wired_airgap.md %}
The BitBox02 has no camera and no microSD slot, so every interaction goes over USB.
That is why it is not on this guide's recommended list, despite being a well-regarded device.

#### Secure Chip Firmware Is Closed
The main firmware is open source, but the secure element runs closed code, as on most devices with one.

{% include hw/encouragement.md %}
