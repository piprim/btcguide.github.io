---
title: Specter-Desktop
description: Specter-Desktop stores wallet data in plain text despite its password. Encrypt your disk and backups, use a dedicated user, or move the data folder.
---

[Specter-Desktop](https://github.com/cryptoadvance/specter-desktop) is the coordinator software this guide uses, and we still recommend it.
Its known weaknesses are listed here, with what you can do about them.

#### Wallet Data Is Stored in Plain Text
Setting a password in Specter-Desktop only locks its web interface.
Everything Specter knows about your wallets is written to the `.specter` folder in your home directory as plain `json` and `csv` files: your xpubs, your addresses, wallet names and labels.
Your private keys are never there (they stay on your hardware wallets), but anyone or anything that can read your home directory can learn your balances and transaction history without ever seeing the Specter password: another user of the same computer, malicious software, backup tools, or forensic recovery of a discarded drive.
This is tracked in [specter-desktop issue #2672](https://github.com/cryptoadvance/specter-desktop/issues/2672), still open as of 2026.

Until Specter encrypts its data at rest, protect the folder yourself:

* Encrypt your hard drive, as described in [Advanced Computer Configuration](/setup-computer/computer-advanced) (full disk encryption on Ubuntu, `FileVault` on macOS), and make sure any backup that includes the `.specter` folder is encrypted too.
* Run Specter-Desktop under a user account you use for nothing else, and don't share that account with other people or programs.
* If you would rather keep the data on an encrypted volume that you only mount while using Specter, start Specter with an explicit data folder: `--specter-data-folder /path/to/mounted/folder`.
