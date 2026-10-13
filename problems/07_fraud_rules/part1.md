# Fraud Rules Engine: Part 1

You are building the screening engine that sits in front of a card payments network. Every card transaction is checked against a list of fraud rules before it is authorized. Each transaction ends with one of three outcomes: it is approved, declined, or sent to a human analyst for review.

A **rule** has a rule id, a numeric **priority**, an **action** (`DECLINE` or `REVIEW`) and a **condition** on the transaction. Rules are evaluated in ascending priority. When two rules have the same priority, the one whose rule id is smaller in plain character-code (ASCII) order goes first. The first rule whose condition holds decides the outcome, and no further rules are checked. If no rule's condition holds, the transaction is approved.

In this part the engine has exactly four built-in rules:

| Rule id | Priority | Action | Condition |
|---|---|---|---|
| `blocked_card` | 10 | `DECLINE` | the transaction's card is currently on the blocklist |
| `blocked_country` | 20 | `DECLINE` | the transaction's country is one of `CU`, `IR`, `KP`, `SY` |
| `amount_limit` | 30 | `DECLINE` | amount is strictly greater than `1000000` |
| `high_amount` | 40 | `REVIEW` | amount is greater than or equal to `200000` |

The engine also keeps a **blocklist** of cards, which is empty at the start. Risk analysts add and remove cards with `BLOCK_CARD` and `UNBLOCK_CARD`. A card does not need to have appeared in any transaction before it is blocked.

## Commands

Each command is a single string. Tokens are separated by exactly one space, and there are no leading or trailing spaces. The first token is always a timestamp: a non-negative integer of at most `10^9`. Timestamps are always well formed and never decrease from one command to the next. The second token is the command name. Command names are case sensitive. **Every command produces exactly one output line.**

These formats are used throughout:

- An **identifier** is 1 to 32 characters. Each character is an ASCII letter (`A` to `Z`, `a` to `z`), a digit (`0` to `9`) or an underscore (`_`). Identifiers are case sensitive, so `c_1` and `C_1` are different cards.
- An **integer** is one or more ASCII digits `0` to `9` and nothing else: no sign, no decimal point, no separators, no exponent. Leading zeros are allowed and ignored, so `0050` is 50.
- A **country** is exactly two uppercase ASCII letters `A` to `Z`. Any such pair is accepted, even if it is not a real country code.

| Command | Format | Output |
|---|---|---|
| Transaction | `<ts> TXN <txn_id> card=<card> amount=<amount> merchant=<merchant> country=<country>` | `APPROVE`, `DECLINE <rule_id>`, `REVIEW <rule_id>`, `DUPLICATE` or `INVALID` |
| Block a card | `<ts> BLOCK_CARD <card>` | `OK`, `ALREADY_BLOCKED` or `INVALID` |
| Unblock a card | `<ts> UNBLOCK_CARD <card>` | `OK`, `NOT_BLOCKED` or `INVALID` |

### TXN

`txn_id`, `card` and `merchant` are identifiers. `amount` is an integer number of cents between `1` and `10^9` inclusive. `country` is a country.

After `<txn_id>` come exactly four field tokens of the form `key=value`. The keys are `card`, `amount`, `merchant` and `country`, and **they may appear in any order**. Each field token is split at its first `=` character: the part before it is the key and the part after it is the value. Keys are case sensitive.

A TXN command is **invalid** if any of the following holds:

- it does not have exactly 7 tokens (timestamp, `TXN`, txn id, four fields)
- `txn_id` is not an identifier
- a field token contains no `=`, or its key is not one of the four keys above
- a key appears more than once (and so some other key is missing)
- a value is malformed: `card` or `merchant` is not an identifier, `amount` is not an integer or is outside `1` to `10^9`, `country` is not a country

An invalid TXN outputs `INVALID` and has no effect. Its txn id is not used up.

If the command is valid but `txn_id` equals the id of a transaction that was evaluated earlier (whatever its outcome), the output is `DUPLICATE` and the command has no effect. Validity is checked before duplication, so a malformed command that repeats an old id outputs `INVALID`.

Otherwise the transaction is evaluated against the rules as described above and the output is one of:

- `DECLINE <rule_id>` if the deciding rule's action is `DECLINE`
- `REVIEW <rule_id>` if the deciding rule's action is `REVIEW`
- `APPROVE` if no rule's condition holds

### BLOCK_CARD and UNBLOCK_CARD

Both take exactly one argument, a card identifier. Any other token count, or an argument that is not an identifier, outputs `INVALID`.

- `BLOCK_CARD` adds the card to the blocklist and outputs `OK`. If the card is already blocked it outputs `ALREADY_BLOCKED` and nothing changes.
- `UNBLOCK_CARD` removes the card from the blocklist and outputs `OK`. If the card is not blocked it outputs `NOT_BLOCKED` and nothing changes.

Changes to the blocklist only affect transactions evaluated after the command.

### Invalid commands

A command whose name is not `TXN`, `BLOCK_CARD` or `UNBLOCK_CARD` (exact case) outputs `INVALID` and has no effect. Invalid commands of any kind never change any state.

## Function Description

Complete the function `evaluateTransactions` in the editor below.

`evaluateTransactions` has the following parameter:

- `string commands[n]`: the commands, in chronological order

Returns:

- `string[]`: exactly one output line per command, in the same order as the commands

## Constraints

- `1 ≤ n ≤ 10^4`
- Each command has at most 300 characters and contains only printable ASCII characters.
- Each command starts with a valid timestamp between `0` and `10^9`, followed by a space and at least one more token. Timestamps are non-decreasing.

## Input Format For Custom Testing

The first line contains an integer, `n`, the number of commands.
Each of the next `n` lines contains a string, `commands[i]`.

## Sample Case 0

### Sample Input For Custom Testing

```
8
1 TXN t1 card=c_100 amount=2500 merchant=m_coffee country=US
2 TXN t2 card=c_100 amount=250000 merchant=m_tv country=US
3 TXN t3 card=c_200 amount=4000 merchant=m_food country=KP
4 BLOCK_CARD c_100
5 TXN t4 card=c_100 amount=100 merchant=m_coffee country=US
6 UNBLOCK_CARD c_100
7 TXN t5 card=c_100 amount=1500000 merchant=m_car country=CA
8 TXN t1 card=c_300 amount=500 merchant=m_book country=GB
```

### Sample Output

```
APPROVE
REVIEW high_amount
DECLINE blocked_country
OK
DECLINE blocked_card
OK
DECLINE amount_limit
DUPLICATE
```

### Explanation

- `t1`: 2500 cents from the US. No rule matches, so the output is `APPROVE`.
- `t2`: 250000 is at least 200000 but not above 1000000, so the first matching rule is `high_amount`, giving `REVIEW high_amount`.
- `t3`: the country `KP` is blocked, so the output is `DECLINE blocked_country`.
- `BLOCK_CARD c_100` adds the card to the blocklist: `OK`.
- `t4`: card `c_100` is blocked. `blocked_card` has priority 10, so it is checked first and the output is `DECLINE blocked_card`.
- `UNBLOCK_CARD c_100` removes the card: `OK`.
- `t5`: 1500000 is above 1000000. Both `amount_limit` (priority 30) and `high_amount` (priority 40) match, and `amount_limit` comes first, giving `DECLINE amount_limit`.
- The last command reuses the id `t1`, so the output is `DUPLICATE`.

## Sample Case 1

### Sample Input For Custom Testing

```
9
10 TXN t1 country=BR amount=200000 merchant=m_9 card=c_1
11 TXN t2 card=c_1 amount=12.50 merchant=m_9 country=BR
12 TXN t2 card=c_1 amount=1250 merchant=m_9 country=br
13 TXN t2 card=c_1 amount=1250 merchant=m_9 country=BR
14 BLOCK_CARD c_1
15 BLOCK_CARD c_1
16 TXN t3 card=c_1 amount=99 merchant=m_9 country=IR
17 UNBLOCK_CARD c_2
18 REFUND t3
```

### Sample Output

```
REVIEW high_amount
INVALID
INVALID
APPROVE
OK
ALREADY_BLOCKED
DECLINE blocked_card
NOT_BLOCKED
INVALID
```

### Explanation

- `t1`: the fields are in a different order, which is allowed. The amount is exactly 200000, and the `high_amount` threshold is inclusive, so the output is `REVIEW high_amount`.
- The first `t2` has amount `12.50`. That is not an integer, so the output is `INVALID`.
- The second `t2` has country `br`. That is not two uppercase letters, so the output is `INVALID`.
- The third `t2` is valid. The two earlier `t2` commands were invalid and did not use up the id, so this is not a duplicate. No rule matches: `APPROVE`.
- `BLOCK_CARD c_1` outputs `OK`. Repeating it outputs `ALREADY_BLOCKED`.
- `t3`: card `c_1` is blocked and country `IR` is blocked too. `blocked_card` has the lower priority number, so the output is `DECLINE blocked_card`.
- `UNBLOCK_CARD c_2`: that card was never blocked, so the output is `NOT_BLOCKED`.
- `REFUND` is not a known command: `INVALID`.
