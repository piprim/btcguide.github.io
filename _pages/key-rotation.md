---
title: Key Rotation
no_advanced_link: true
---

Key rotation means replacing one (or more) of the keys in your multisig with a brand new seed, and moving your funds to the resulting new wallet.
A multisig wallet is defined by its exact set of public keys, so you cannot "edit" a key in place: changing one means creating a new wallet and sending the coins to it.

#### When to Rotate
Rotate a key as soon as any of these happens:

* A seed backup may have been seen by someone else (a break-in, a lost safe deposit box, a family member who should no longer have access).
* A hardware wallet is lost or stolen **and** you are not confident its PIN will hold up.
* A device is known to have generated weak seeds, like the [Coldcard bug](/known-issues/hardware/coldcard).
* Someone who held a key for you (a friend, a lawyer, a business partner) leaves that role.
* A key has been loaded into a hot wallet, for example after an [emergency recovery](/emergency-recovery) through Electrum.
Treat that key as hot from then on.

With a `2-of-3`, one compromised key cannot spend your coins, so there is no need to panic.
A second compromise would, so rotate promptly rather than eventually.

#### How to Rotate
1. Generate a new seed on a new (or freshly wiped and updated) hardware wallet, following the [setup steps](/setup-wallets/) for that device, and back it up like the others.
1. In Specter-Desktop, add the new device, then create a *new* multisig wallet (e.g. `Redundant Multisig v2`) from the two keys you are keeping plus the new one.
Do not delete the old wallet yet.
1. Register the new wallet on each hardware wallet, exactly as in [Coordinate Multisig](/setup-wallets/coordinate-multisig).
1. Verify a receive address of the new wallet on your hardware wallets, as in [Verify Receive Address](/verify-receive-address/).
1. Send the entire balance of the old wallet to that address, signing with 2 keys as in [Send Bitcoin](/send-bitcoin).
Consider a small test amount first; with many unspent outputs this may take a few transactions.
1. Back up the new wallet's [public keys](/backup-wallet/public-keys) and update any instructions you left for heirs.
1. Once the old wallet is empty and the transactions have confirmed, you may delete it from Specter-Desktop and destroy the retired seed backup.

Coins sent to one of the *old* wallet's addresses in the future would still land in the old wallet, so keep its public-key backup until you are sure nobody will reuse an old address.

{% include next_steps.md %}
