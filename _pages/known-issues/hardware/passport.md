---
title: Passport
description: Known issues with the Foundation Passport Prime, including the discontinued Passport Core, airgap limits, firmware that is not yet reproducible and account lock-in.
---

Foundation's [Passport Prime](https://foundation.xyz/products/passport-prime) is a bitcoin hardware wallet with a secure element, a camera for QR codes and a microSD slot.
It can export a multisig configuration as a descriptor QR code or file, and users report multisig working with Sparrow.
It is the most polished device on this guide's [list of alternatives](/equipment#choosing-the-second-hardware-wallet), and also the most expensive.

#### Passport Core Is Discontinued
The earlier Passport Core was a strictly airgapped, QR-and-microSD-only device and would have been the natural Coldcard replacement for this guide.
Foundation discontinued it in July 2026 and every Core link on their site now redirects to the Prime.
If you own a Core, keep using it: Foundation says security updates continue for now, and Core seeds can be imported into a Prime later.

#### Not Strictly Airgapped
The Prime ships with Bluetooth (which Foundation calls QuantumLink) and NFC for its Envoy phone app.
Encrypted radio is not an airgap.
We found no documentation on disabling the radios entirely, so treat the device as having a wireless attack surface and use QR or microSD for all transfers regardless.

#### Firmware Not Yet Reproducible
Foundation publishes the Prime's firmware source, but at the time of writing shipped binaries cannot be reproduced from it, so you are trusting that the signed binary matches the code.

#### Account Lock-In
A Prime account paired with one companion wallet does not load in another.
Keep your [public key backup](/backup-wallet/public-keys) current so recovery never depends on the Prime's own export.

#### Specter-Desktop Support Unconfirmed
Foundation's Prime documentation names no coordinators and says Core integrations do not imply Prime compatibility.
Sparrow works; before buying, confirm with Foundation that Specter-Desktop does too, or plan to use Sparrow as your coordinator.

{% include hw/encouragement.md %}
