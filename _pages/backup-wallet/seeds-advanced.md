---
title: Backup Seeds
---

## Think Hard About Your Risks
It is a natural human bias to believe theft is a greater risk than loss, despite data indicating the opposite.
(An analogy that gives some insight into the relevant psychology: we are all terrified of homicide despite suicide being more common.)
Non-expert users should question themselves when taking extreme steps to protect against theft over loss.

There are many tradeoffs between security/redundancy below and only you can decide what the appropriate balance is for your needs.

## Multiple Locations

#### Physical Security
Not only does storing all of your bitcoin information in one place make it less secure, it also makes you a target!
You don't want a home-invader to be able to hold you at gunpoint for your life-savings.
The downside is that funds secured by a "geographically split" scheme will be harder to spend because you must visit multiple secure locations to gather signatures.
_For day-to-day funds, you might choose a simpler single-key signature wallet setup that is easy to spend_ (but not as secure).

#### Natural Disasters
If you keep all `m` seeds in one location and there is a fire (or flood) you could lose everything, perhaps when you need it most.
In the unlikely event you need to evacuate, you don't also want to be carrying your life-savings on you (see previous section on physical security).

Imagine you have a `2-of-3` scheme with 1 seed in each of 3 cities (A, B, and C).
Should you need to evacuate city A, you can take seed A with you to city B or to city C.
As you are only carrying 1 (of a needed 2) seeds, if you are robbed during this time your attacker will be unable to spend your bitcoin.
Important note: in the event a seed is compromised you need to retrieve `m` seeds ASAP to "rotate" out the seed that was stolen (this is accomplished by moving your funds to a new multisig scheme where you control *all* 3 seeds again).


## Example Layouts
There is no single right answer, but here is a starting point for the 5 items of a `2-of-3` (2 hardware wallets, 3 seed backups) and the 10 items of a `3-of-5`.
A hardware wallet and its own seed backup are the same key, so they may share a row in the "key" column but should not share a location.

| Key | `2-of-3` device | `2-of-3` seed backup |
|-----|-----------------|----------------------|
| A   | Home safe | Second spot on your property |
| B   | Home safe | Safe-deposit box, bank 1 |
| C   | (paper wallet, no device) | Trusted family member or friend, another city |

Note that the home safe holds 2 devices, which is a quorum on its own if both PINs fall; keep device B elsewhere (workplace safe, second residence) if you can.

| Key | `3-of-5` location |
|-----|-------------------|
| A   | Home safe |
| B   | Second spot on your property or second residence |
| C   | Safe-deposit box, bank 1 |
| D   | Safe-deposit box, bank 2 (different institution) |
| E   | Trusted family member, friend or lawyer, another city |

Two seeds at home in a `3-of-5` largely defeats the point of the larger quorum; if you cannot manage 5 locations, stick with `2-of-3`.
Keep `m - 1` keys outside your home region so an evacuation does not strand you.

## Estate Planning
Moved to its own page: [Inheritance](/inheritance).

## Protect Your Backups

#### Metal
Use durable [metal for bitcoin seed storage](https://blog.lopp.net/metal-bitcoin-seed-storage-stress-test-round-iii/) instead of paper, which can fade, burn, or smudge.

#### Archival Paper & Ink
[Archival paper](https://en.wikipedia.org/wiki/Acid-free_paper#Archival_paper) is obviously not as durable as metal, but better than regular paper.
Place your paper into a plastic bag with a good seal (vacuum sealed even better) so that it doesn't get destroyed in the event of water damage.

#### Fireproof Document Bag
You can use these to protect seed backups, and also to protect your physical hardware wallets.


{% include next_steps.md next_url="/backup-wallet/public-keys" next_name="Backup Public Keys" %}

