---
title: Configure Computer
description: Install Ubuntu on the computer that will run your multisig coordinator, and what level of caution this machine actually needs.
---

#### A Note on Caution
In a perfect world, you'd carefully verify the software you're installing.
However, since this machine won't store private key material\* (and multiple signatures will be required to move funds) it may be acceptable for you to install software that seems correct without properly verifying it using the command-line.

_\*While we recommend that no private key material ever touch this machine, that setup is slightly more involved and thus you may choose to generate 1 seed on this machine (and then wipe it after).
Remember that this alone is not sufficient to steal/lockup funds, so it may present an acceptable tradeoff for smaller HODLers.
For more details, see [Paper Wallet Setup steps](/setup-wallets/paper)._

## Install Ubuntu

#### Why Ubuntu?
This guide assumes a dedicated machine running Ubuntu for three reasons:

1. Linux is far more secure than closed-source operating systems like Mac and Windows, and Ubuntu is the most popular (and arguably most beginner-friendly) distribution.
1. Developers use it heavily, so it has the best compatibility with bitcoin tools.
1. It raises the bar slightly, which keeps away the users most likely to hurt themselves.

Advanced users can follow this guide on Mac or Windows, but you are on your own for the differences.
A fresh install of another operating system is better than a long-used daily driver, but still a weaker choice than a dedicated Ubuntu machine.

You'll want to download and install the latest Long-Term Support (LTS) version of [Ubuntu Desktop](https://ubuntu.com/download/desktop) (currently `20.04.1`).
Put the installer on a USB stick or burn it onto a DVD.
Both options are good, though we find DVDs are slightly preferable as they are slightly more secure and don't take up a USB port.
See [these step-by-step instructions](https://ubuntu.com/tutorials/install-ubuntu-desktop).



{% include next_steps.md next_url="/setup-computer/bitcoin-node" next_name="Configure Your Bitcoin Node" %}
