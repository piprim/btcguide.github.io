---
title: Common Hosted Service Issues
description: Shortcomings shared by hosted multisig services, explained once: limited hardware support, reintroduced single points of failure, privacy, and how to weigh them.
---

Hosted multisig services share the same shortcomings.
Each service page in this guide names them and links here for the full explanation.

## Limited Hardware Wallet Support
Hosted services only work with the hardware wallets they have integrated, and that list lags behind what the wider ecosystem supports.
Support has improved since this guide was written (Casa, for example, now supports [Keystone](/known-issues/hardware/keystone)), so check the service's current device list before buying hardware.
**Properly verifying a receive address is still only possible for advanced users**, and depending on the device may require plugging your hardware wallet into your phone or computer, adding another potential attack vector.

## Could Reintroduce Single Points of Failure
Proper multisig allows you to have no single points of failure (see section title [Why Multisig](/why-multisig)), but it still requires you take some control of your financial sovereignty.
Users who rely on third-party services may accidentally reintroduce a single points of failure.
For example, if a `2-of-3` service holds 1 of your keys and mails you 1 (malicious) hardware wallet they are in a trusted position as they could control a majority of your keys!

More realistically, were a multisig service provider to be hacked they might be able to exploit the trust users have in them.
We've seen [similar attacks](https://cointelegraph.com/news/electrum-bitcoin-wallet-still-plagued-by-known-crypto-phishing-attack) on the popular Electrum Client for many years.
This might take the form of an invalid receive address (if using a stateless hardware wallet with limited defenses) or an invalid change address (if using a hardware wallet that can't detect change attacks).

## Privacy Alert
Any third party service that can participate/coordinate multisig transactions will have access to your balance and transaction history.
They may be forced to share your records with multiple government agencies, and often be legally unable to disclose their compliance with requests.
Of course most bitcoiners buy their coins on exchanges that follow KYC/AML procedures, so this may or may not be a factor for your use-case.

## Evaluate the Service in Totality
The service pages are about known issues, not positive attributes.
No setup is 100% secure.

Hosted multisig providers make multisig much more accessible/easier for less technically savvy HODLers.
They will likely continue to improve over time and have an incentive to push best practices onto their users.
When performed correctly, the hosting provider is unable to censor/steal funds and can only assist you in recovering your own funds.
