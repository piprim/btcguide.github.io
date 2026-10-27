---
title: Emergency Recovery
description: Precautions when recovering with a Trezor or Sparrow, including firmware updates, an airgap machine, moving the PSBT by QR and verifying downloads.
---

## Option A - Trezor Hardware Wallet

#### Update Your Firmware
TODO: add content

#### Do Not Disclose Your Addresses
TODO: add content

## Option C - Sparrow Software Wallet

#### Use an Airgap Machine
Sparrow is not included in Tails, so use a dedicated machine instead: boot an Ubuntu live USB (or a freshly wiped install) with networking off, and never connect it to the internet while a seed is loaded.
On a separate online computer, download the Sparrow release for Linux plus its manifest and signature from [the Sparrow download page](https://sparrowwallet.com/download/), verify them following the instructions on that page, and carry the installer over on a USB drive.
Sparrow runs fine without a node connection; it will simply show the wallet as offline, which is all you need to sign.

#### Move the PSBT by QR Code
In step 8 on the previous page, instead of carrying the PSBT (Partially Signed Bitcoin Transaction) on a USB or SD card, show it as a QR code in Specter-Desktop and scan it with the airgapped machine's webcam using Sparrow's `Scan QR`.
After signing, Sparrow's `Show QR` displays the signed PSBT, which Specter-Desktop can scan back.
You may need to adjust distance and lighting before the animated code scans cleanly.

#### Verify the Sparrow Download
Sparrow releases are signed by its developer; the [download page](https://sparrowwallet.com/download/) explains how to check the signature with `gpg` and the manifest with `sha256sum`.
Do this on the online machine before copying the installer to the airgapped one.

