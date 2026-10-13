# Merchant Payouts: Part 1

You are building the balance ledger behind a payments platform. Merchants are onboarded with a settlement currency. When a merchant charges a customer, the platform keeps a processing fee and credits the rest (the **net** amount) to the merchant. Money does not become spendable right away: each charge's net amount is first **pending**, and it becomes **available** two days later. Merchants can then withdraw available money to their bank account with a **payout**.

Each merchant has two balances, both starting at `0.00`:

- **available**: money that can be paid out.
- **pending**: net amounts of charges that have not settled yet.

The processing fee for a charge with gross amount `g` is `g × 0.029 + 0.30`, rounded to 2 decimal places with **round half up** (a third decimal digit of exactly 5 rounds up, for example `0.445` becomes `0.45`). The net amount is `g - fee`. All money values in this problem are exact decimals with at most 2 decimal places; do not use binary floating point.

A charge made at timestamp `t` **settles** at timestamp `t + 172800` (two days). Settlement is inclusive: a command whose timestamp is greater than or equal to `t + 172800` sees that charge's net amount in **available**; a command whose timestamp is smaller sees it in **pending**. Nothing happens between commands, so you only need to account for settlement when a command is processed.

## Commands

Each command is a single string of tokens separated by exactly one space, with no leading or trailing spaces. The first token is a Unix timestamp in seconds, the second token is the command name, and the remaining tokens are the arguments. Command names are case sensitive. Every command produces exactly one output line.

| Command | Format | Output |
|---|---|---|
| ONBOARD | `<ts> ONBOARD <merchant_id> <currency>` | `ONBOARDED <merchant_id>` |
| CHARGE | `<ts> CHARGE <merchant_id> <charge_id> <amount> <currency>` | `CHARGED <charge_id> fee=<fee> net=<net>` |
| BALANCE | `<ts> BALANCE <merchant_id>` | `available=<available> pending=<pending>` |
| PAYOUT | `<ts> PAYOUT <merchant_id> <amount>` | `PAID <payout_id> <amount>` |
| any invalid command | | `INVALID` |

### Token formats

- `merchant_id`: 1 to 20 characters, each a lowercase letter `a`-`z`, a digit `0`-`9` or an underscore `_`.
- `currency`: exactly 3 uppercase letters `A`-`Z`.
- `charge_id`: the prefix `ch_` followed by 1 to 20 characters, each an ASCII letter (either case) or a digit. Charge ids are case sensitive (`ch_a` and `ch_A` are different).
- `amount`: one or more digits `0`-`9`, optionally followed by a `.` and then exactly one or two digits. Leading zeros are allowed (`007` means `7.00`, `00.50` means `0.50`). Anything else is malformed, for example `.5`, `5.`, `1.234`, `-5`, `+5`, `1e3`, `1,000` or `$5`.

Money in the output is always printed with exactly 2 decimal places, no thousands separators and no plus sign (for example `0.19`, `1000.00`). A negative value (possible in later parts) is printed with a leading `-`, for example `-3.20`. A zero value is always printed as `0.00`.

### ONBOARD

Creates merchant `merchant_id` with settlement currency `currency` and both balances at `0.00`. Output: `ONBOARDED <merchant_id>`.

### CHARGE

Records a successful charge of `amount` (the gross amount) for merchant `merchant_id`. The fee and net amount are computed as described above, and the net amount is added to the merchant's pending balance until it settles at `ts + 172800`. Output: `CHARGED <charge_id> fee=<fee> net=<net>`.

Charge ids are unique across the whole platform: once a charge id has been used by a successful CHARGE (for any merchant), any later CHARGE with the same id is invalid. A charge id used only by invalid commands is not taken.

### BALANCE

Output: `available=<available> pending=<pending>` for the merchant at the command's timestamp.

### PAYOUT

Moves `amount` out of the merchant's available balance. Pending money can never be paid out. On success the payout gets the id `po_<k>`, where `k` is 1 for the first successful payout on the platform, 2 for the second, and so on (one counter shared by all merchants). Output: `PAID <payout_id> <amount>`, with the amount printed in the money format above.

### Invalid commands

A command is invalid, outputs `INVALID` and changes nothing if any of the following is true:

- The command name is not one of the commands above (matching is case sensitive, so `balance` is invalid).
- The number of arguments is not exactly the number shown in the format.
- ONBOARD: `merchant_id` or `currency` is malformed, or the merchant already exists.
- CHARGE: the merchant does not exist; `charge_id` is malformed or already used; `amount` is malformed or less than `0.50`; or `currency` is not exactly equal to the merchant's currency.
- BALANCE: the merchant does not exist.
- PAYOUT: the merchant does not exist; `amount` is malformed or equal to zero; or `amount` is greater than the merchant's available balance at the command's timestamp. Paying out exactly the available balance is allowed.

## Function Description

Complete the function `processPayoutCommands` in the editor below.

`processPayoutCommands` has the following parameter:

- `string commands[n]`: the commands, in chronological order

Returns:

- `string[]`: one output line per command, in the order the commands are given

## Constraints

- `1 ≤ n ≤ 10^4`
- Every command contains at least two tokens, and the first token is always a valid integer timestamp `ts` with `1 ≤ ts ≤ 2 × 10^9`.
- Timestamps are non-decreasing. Several commands may share a timestamp; they are processed in input order.
- The last timestamp minus the first timestamp is at most `5 × 10^7`.
- Every token consists of printable ASCII characters without spaces and is at most 25 characters long.
- At most 100 ONBOARD commands succeed.
- Every well-formed amount token (including `percent` and `minimum` in later parts) has a value below `10^9`.

## Input Format For Custom Testing

The first line contains an integer, `n`, the number of commands.
Each of the next `n` lines contains a string, `commands[i]`.

## Sample Case 0

### Sample Input For Custom Testing

```
8
1767225600 ONBOARD acme USD
1767225660 CHARGE acme ch_1 100.00 USD
1767225720 CHARGE acme ch_2 5.00 USD
1767225780 BALANCE acme
1767225900 PAYOUT acme 10.00
1767398460 BALANCE acme
1767398460 PAYOUT acme 50
1767484800 BALANCE acme
```

### Sample Output

```
ONBOARDED acme
CHARGED ch_1 fee=3.20 net=96.80
CHARGED ch_2 fee=0.45 net=4.55
available=0.00 pending=101.35
INVALID
available=96.80 pending=4.55
PAID po_1 50.00
available=51.35 pending=0.00
```

### Explanation

- `acme` is onboarded with currency USD.
- Charge `ch_1` of `100.00`: fee is `100.00 × 0.029 + 0.30 = 3.20`, net `96.80`. It settles at `1767225660 + 172800 = 1767398460`.
- Charge `ch_2` of `5.00`: `5.00 × 0.029 + 0.30 = 0.445`, which rounds half up to `0.45`, so the net is `4.55`. It settles at `1767398520`.
- BALANCE: nothing has settled yet, so available is `0.00` and pending is `96.80 + 4.55 = 101.35`.
- PAYOUT of `10.00` is invalid because the available balance is `0.00`.
- At `1767398460`, `ch_1` has settled (the boundary is inclusive) but `ch_2` has not: `available=96.80 pending=4.55`.
- PAYOUT of `50` succeeds as the first payout on the platform, `po_1`, printed as `50.00`. Available becomes `46.80`.
- At `1767484800` both charges have settled: available is `46.80 + 4.55 = 51.35`.

## Sample Case 1

### Sample Input For Custom Testing

```
13
1767225600 ONBOARD shop_1 EUR
1767225600 ONBOARD shop_1 USD
1767225610 ONBOARD Shop2 USD
1767225620 CHARGE shop_1 ch_a 0.49 EUR
1767225630 CHARGE shop_1 ch_a 0.50 EUR
1767225640 CHARGE shop_1 ch_b 20.00 USD
1767225650 CHARGE shop_1 ch_b 12.345 EUR
1767225660 CHARGE shop_1 ch_b 12.5 EUR
1767225670 BALANCE ghost
1767225680 balance shop_1
1767225690 BALANCE shop_1
1767398429 BALANCE shop_1
1767398430 PAYOUT shop_1 0.19
```

### Sample Output

```
ONBOARDED shop_1
INVALID
INVALID
INVALID
CHARGED ch_a fee=0.31 net=0.19
INVALID
INVALID
CHARGED ch_b fee=0.66 net=11.84
INVALID
INVALID
available=0.00 pending=12.03
available=0.00 pending=12.03
PAID po_1 0.19
```

### Explanation

- `shop_1` is onboarded with EUR. Onboarding it again is invalid, and `Shop2` is invalid because merchant ids may not contain uppercase letters.
- `0.49` is below the minimum charge amount of `0.50`, so that CHARGE is invalid and `ch_a` stays unused.
- `ch_a` for `0.50` succeeds: `0.50 × 0.029 + 0.30 = 0.3145`, fee `0.31`, net `0.19`.
- `ch_b` in USD is invalid because the merchant's currency is EUR. `12.345` has three decimal places, so it is malformed.
- `ch_b` for `12.5` succeeds: `12.50 × 0.029 + 0.30 = 0.6625`, fee `0.66`, net `11.84`.
- `ghost` does not exist and `balance` is not a command name (names are case sensitive), so both are invalid.
- Pending is `0.19 + 11.84 = 12.03`.
- `ch_a` was charged at `1767225630` and settles at `1767398430`. At `1767398429` it is still pending.
- At `1767398430` the `0.19` is available, and a payout of exactly the available balance succeeds as `po_1`.
