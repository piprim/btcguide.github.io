---
title: Sparrow
---

[Sparrow](https://sparrowwallet.com/) is a free, open-source desktop wallet with first-class multisig support.
It works with every hardware wallet in this guide, over USB or QR codes, and can do everything the guide does with [Specter-Desktop](https://github.com/cryptoadvance/specter-desktop): create the multisig wallet from your three public keys, verify receive addresses, build and sign PSBTs, and connect to your own Bitcoin Core node.
This guide was written around Specter-Desktop in 2021; today Sparrow is the more widely used and more actively maintained of the two, and the guide's newer pages ([emergency recovery](/emergency-recovery), [inheritance](/inheritance)) already rely on it.
If you are starting fresh, Sparrow is a sound choice as your coordinator.

Where Sparrow is better:

* Regular releases and an active developer, which the [Electrum](electrum) page explains is a hard requirement for mission-critical software.
* Wallet files are encrypted on disk when you set a password, unlike [Specter-Desktop's plain text data folder](specter).
* Tor is built in, and a single `Server` setting points it at your own Bitcoin Core or Electrum server.

Where it falls short of Specter-Desktop:

#### No Web Interface
Sparrow is a desktop application only.
Specter-Desktop runs as a web server, so you can keep it on the same machine as your Bitcoin Core node and use it from a browser on another computer.
With Sparrow, the coordinator runs on the computer in front of you, so follow the [computer setup](/setup-computer) steps for that machine.

#### Public Servers by Default
On first run Sparrow offers to connect to a public Electrum server.
That is convenient, but it reveals your addresses and balances to whoever runs the server, exactly the problem described on the [Electrum](electrum) page.
Pick `Bitcoin Core` in `Preferences` > `Server` and point it at your own node before importing any key.

#### Java Desktop Application
Sparrow is written in Java and ships its own runtime, so the download is large and the interface looks different from native apps.
This is cosmetic; the releases are signed, and the [download page](https://sparrowwallet.com/download/) explains how to verify them.
