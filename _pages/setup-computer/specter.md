---
title: Install Specter-Desktop
description: Download Specter-Desktop and connect it to your Bitcoin Core node. Sparrow is a fully supported alternative coordinator.
---

This guide uses Specter-Desktop as the coordinator, the software that combines your hardware wallets into one multisig wallet.
[Sparrow](https://sparrowwallet.com/) is a fully supported alternative, more widely used and more actively maintained today; see its [known issues](/known-issues/software/sparrow) for a comparison.
Everything that follows works with either.

#### Download
Grab the latest release of the `Specter-Desktop` app:  
<https://github.com/cryptoadvance/specter-desktop/releases>

For Windows the installer is `specter_desktop_setup.exe` and for macOS it is `SpecterDesktop-v0.x.x.dmg` (where `x.x` represent the current version number).

#### Connect Specter-Desktop to Your Bitcoin Core Node
If Bitcoin Core is running on the same computer as Specter-Desktop, then Specter-Desktop should automatically detect authentication info from the default Bitcoin Core data directory.

![](/assets/img/setup-specter-detect-node.png){:width="85%" class="border_image"}


{% include next_steps.md next_url="/setup-wallets" next_name="Setup Hardware Wallets" %}
