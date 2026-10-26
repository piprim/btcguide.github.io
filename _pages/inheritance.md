---
title: Inheritance
no_advanced_link: true
---

Nothing happens to your bitcoin when you die.
There is no account to recover, no company to call, and no court order that can open a wallet.
If nobody who outlives you can gather a quorum of your seeds *and* understands what they are, the coins are gone forever.
In practice heirs fail on knowledge far more often than on access: the seed was in the safe all along, but nobody knew what it was for.

Multisig is the best tool we have for this.
You can give several people partial access without any one of them being able to spend, and you can rehearse the whole recovery while you are alive.

#### What Your Heirs Need
Everything on this list, or the rest is useless:

1. **A quorum of seeds** (`m` of your `n`), which they must be able to reach without you.
1. **Your [public key backup](/backup-wallet/public-keys)**, the fingerprints, derivation paths and `Zpub` of all `n` keys.
Without it, seeds alone cannot rebuild the wallet. Keep a copy with every seed.
1. **A recovery letter** (below) telling them what all of this is.
1. **Someone technical enough to follow it**, or the name of one they can hire.

#### The Recovery Letter
Write a plain-language letter and keep a copy with each seed backup and with your will.
It must not contain any seed words, so it is safe for it to be read.
It should say:

* What this is: "a 2-of-3 multisig bitcoin wallet; any two of the three seeds listed here can spend it".
* Which seed is which: `Seed A - Keystone, at home safe`, `Seed B - Coldcard, bank box at ...`, `Seed C - paper wallet, with ...`, with the name and contact details of each holder.
* Where the public key backup is.
* Which software to use and how, in a few lines: install Sparrow (or Specter-Desktop), create a 2-of-3 wallet from the three public keys, enter two seeds, send everything to a new wallet.
A link to the [Emergency Recovery](/emergency-recovery) page of this guide is a good shortcut.
* Who to ask for help, and the rough value at stake so they take it seriously.

Update the letter whenever you [rotate a key](/key-rotation) or a holder changes.

#### A Worked Example
**Anyone** who has a quorum of seeds _can_ spend your bitcoins! (even if they _don't_, it's important to know that they _can_)
Depending on your personal situation, this may be a good thing (perhaps a spouse who you want to have complete access) or a bad thing (perhaps a financial manager who might be tempted to steal).

Imagine you have a `2-of-3` scheme with seeds A, B, and C, all of which you initially control.
You and your spouse want to always have access to your bitcoins, and you want your children to only get access in the event both you and your spouse are dead.

You might do the following:

* Give your family (you, your spouse, and your children) a copy of seed A. You/spouse store seed A at home or work and your children also store seed A somewhere that only they have access to (perhaps their home, work, or a safe-deposit box).
* Put seed B in a safe-deposit box that only you and your spouse have access to.
* Give seed C to your lawyer or other trusted-friend, to share with your children only after the death of you and your spouse. They will also share it with you if needed as part of an emergency recovery.

As a result of this scheme:

* You and your spouse always have regular access via seeds A & B, provided that you didn't lose your copy of seed A and that you can get into your safe-deposit box for seed B. If you lose seed A, you can ask your spouse or children for their copy as a backup. In the event of a problem retrieving seed B from the bank, you can ask your lawyer for assistance in recovery (as they have seed C). Keep in mind that if you lose *both* seeds A and B, your bitcoins are permanently lost.
* In the event both you and your spouse die, your children can recover. They already have seed A, they just need seed B (from the bank) or seed C (from the lawyer). They can get access to seed B by contacting the bank (assuming you designated your children as the next-of-kin for your safe-deposit box) or seed C by contacting the lawyer.

Of course, there are many tradeoffs/choices to be made:

* If *both* your lawyer and the bank are dishonest (or compelled by a government order), they can collude to steal your bitcoin (they have access to seeds B and C)!
* If *both* your lawyer and the bank are unlucky/negligent (perhaps they both suffer catastrophic fires in the same day!), you can be locked out of your bitcoin forever (seeds B and C are lost, as seed A alone is not enough to meet the `2-of-3` threshold).
* If your children want to steal their inheritance before you die and are able to collude with (or trick) either the bank or the lawyer, they can get seed B or C and combine it with seed A (which they already have).
* Your lawyer and your children may have some insight into your bitcoin transaction history, which could implicate how much bitcoin you have.

Read more [here](/known-issues/seeds-and-privacy).

#### Rehearse While You Are Alive
Have the person you expect to do the recovery actually do it once, [on testnet](/setup-computer/bitcoin-node-advanced#practice-on-testnet), from the recovery letter alone and without your help.
Every question they have to ask you is a line missing from the letter.
Repeat every few years and whenever the software changes.

#### The Legal Side
* Never put seed words in a will. Wills become public documents during probate.
Have the will refer to the sealed recovery letter and say who holds it.
* A safe-deposit box with named next-of-kin transfers naturally on death; a box only you can open may need a court order first, which is slow but works.
Seeds held by friends or a lawyer need clear written instructions about when to hand them over.
* Think about who could collude: two holders who are also heirs can spend before you die. The example above walks through those risks.
* If you would rather not run this yourself, hosted services such as [Casa](/known-issues/hosted/casa) offer inheritance products built on the same multisig idea, with the trade-offs described on that page.

#### Keep It Current
Do this with your [yearly backup check](/backup-wallet/seeds#check-yearly): confirm every holder still has their seed, still knows what it is, and that the letter still matches reality.
An inheritance plan that was correct five years ago is the most common way to lose everything.

{% include next_steps.md %}
