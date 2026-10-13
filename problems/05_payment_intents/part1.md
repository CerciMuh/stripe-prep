# Payment Intents: Part 1

You are building the core of a card payments API. A merchant collects money through **payment intents**. A payment intent represents one attempt to charge a customer a fixed amount in one currency, and it moves through a small state machine as the merchant confirms it, captures the money and possibly cancels it.

All money is expressed as a whole number of **minor units** of the currency (for example cents for `usd`), so there are no fractions anywhere in this problem.

Every payment intent has an id, an `amount`, a `currency`, a capture method and a state. It also tracks two derived amounts:

- `amount_capturable`: money that has been authorized on the customer's card and can still be captured.
- `amount_received`: money that has actually been collected.

The states are:

| State | Meaning |
|---|---|
| `requires_confirmation` | Created, nothing has happened on the card yet. |
| `requires_capture` | Confirmed with manual capture: the funds are authorized and wait to be captured. |
| `succeeded` | The money has been collected. |
| `canceled` | The intent was canceled. |

The capture method is `automatic` (the default) or `manual`. Confirming an `automatic` intent collects the money immediately. Confirming a `manual` intent only authorizes the funds, and a separate capture collects them.

You receive a chronological list of commands. Process them in order. **Every command produces exactly one output line.**

## Commands

Each command is a single string with exactly three fields separated by `|`:

```
<timestamp>|<action>|<params>
```

- `<timestamp>` is a time in seconds.
- `<action>` is the command name.
- `<params>` is a list of `key=value` pairs separated by `;`, in any order. It may be the empty string, which means there are no parameters.

For example: `1700000000|create|pi=pi_1;amount=5000;currency=usd`.

| Command | Required params | Optional params | Output on success |
|---|---|---|---|
| `create` | `pi`, `amount`, `currency` | `capture_method` | intent line |
| `confirm` | `pi` | none | intent line |
| `capture` | `pi` | none | intent line |
| `cancel` | `pi` | none | intent line |
| `status` | `pi` | none | intent line |

### The intent line

On success every command above outputs the intent's state **after** the command has been applied, in this exact format (single spaces, no trailing space):

```
<pi> <state> <currency> amount=<amount> amount_capturable=<amount_capturable> amount_received=<amount_received>
```

All amounts are printed as plain base 10 integers with no leading zeros and no sign. For example: `pi_1 requires_capture usd amount=5000 amount_capturable=5000 amount_received=0`.

### Command rules

- `create` makes a new intent in state `requires_confirmation` with `amount_capturable=0` and `amount_received=0`. If `capture_method` is omitted it is `automatic`.
- `confirm` is only allowed in state `requires_confirmation`.
  - For an `automatic` intent the state becomes `succeeded` and `amount_received` becomes `amount`.
  - For a `manual` intent the state becomes `requires_capture` and `amount_capturable` becomes `amount`.
- `capture` is only allowed in state `requires_capture`. The state becomes `succeeded`, `amount_received` becomes the previous `amount_capturable`, and `amount_capturable` becomes `0`.
- `cancel` is only allowed in state `requires_confirmation` or `requires_capture`. The state becomes `canceled` and `amount_capturable` becomes `0`.
- `status` changes nothing.

Intent ids are case sensitive: `pi_abc` and `pi_ABC` are different intents. An id can be created only once, even if the intent with that id was later canceled.

### Parsing

Nothing is trimmed: spaces are ordinary characters and all comparisons are exact and case sensitive. A command is **well formed** when all of the following hold:

1. Splitting the command on `|` gives exactly 3 fields.
2. The timestamp field is one or more ASCII digits `0` to `9` (leading zeros are allowed).
3. The action is exactly one of the action names in the table above.
4. If the params field is not empty, splitting it on `;` gives pieces that each contain at least one `=`. The key is the text before the **first** `=` and the value is everything after it (the value may be empty and may itself contain `=`). Every key is non empty. An empty piece, for example from a trailing `;` or from `;;`, has no `=`, so it makes the command malformed.
5. No key appears twice.
6. Every key is allowed for the action (listed as required or optional), and every required key is present.

Parameter values must have these formats:

| Key | Valid value |
|---|---|
| `pi` | `pi_` followed by 1 to 24 ASCII letters or digits (`A` to `Z`, `a` to `z`, `0` to `9`). |
| `amount` | One or more ASCII digits whose integer value is between `1` and `99999999` inclusive. Leading zeros are allowed and ignored, so `0050` means 50. |
| `currency` | Exactly 3 lowercase ASCII letters `a` to `z`. Any such code is accepted. |
| `capture_method` | Exactly `automatic` or `manual`. |

### Errors

A command that fails outputs a single error token and changes nothing. Checks are made in this order and the first failing check decides the output:

1. `ERR_MALFORMED`: the command is not well formed (see Parsing).
2. `ERR_INVALID_PARAM`: any parameter value does not have a valid format.
3. `ERR_DUPLICATE`: `create` with an id that already exists.
   `ERR_NOT_FOUND`: any other command with an id that does not exist.
4. `ERR_INVALID_STATE`: the command is not allowed in the intent's current state.

## Function Description

Complete the function `processPaymentIntents` in the editor below.

`processPaymentIntents` has the following parameter:

- `string commands[n]`: the commands, in chronological order

Returns:

- `string[]`: exactly one line per command, in input order: the intent line on success, otherwise the error token

## Constraints

- `1 ≤ n ≤ 10^4`
- Each command has 1 to 200 characters, all printable ASCII (codes 32 to 126), with no trailing whitespace.
- Every command whose timestamp field is valid has a timestamp value between `1700000000` and `1700600000` inclusive, and these timestamps are non-decreasing in input order.

## Input Format For Custom Testing

The first line contains an integer, `n`, the number of commands.
Each of the next `n` lines contains a string, `commands[i]`.

## Sample Case 0

### Sample Input For Custom Testing

```
8
1700000000|create|pi=pi_1001;amount=5000;currency=usd;capture_method=manual
1700000005|status|pi=pi_1001
1700000010|confirm|pi=pi_1001
1700000020|capture|pi=pi_1001
1700000030|cancel|pi=pi_1001
1700000040|create|currency=eur;amount=1250;pi=pi_1002
1700000050|confirm|pi=pi_1002
1700000060|status|pi=pi_1002
```

### Sample Output

```
pi_1001 requires_confirmation usd amount=5000 amount_capturable=0 amount_received=0
pi_1001 requires_confirmation usd amount=5000 amount_capturable=0 amount_received=0
pi_1001 requires_capture usd amount=5000 amount_capturable=5000 amount_received=0
pi_1001 succeeded usd amount=5000 amount_capturable=0 amount_received=5000
ERR_INVALID_STATE
pi_1002 requires_confirmation eur amount=1250 amount_capturable=0 amount_received=0
pi_1002 succeeded eur amount=1250 amount_capturable=0 amount_received=1250
pi_1002 succeeded eur amount=1250 amount_capturable=0 amount_received=1250
```

### Explanation

- `pi_1001` is created for 5000 `usd` with manual capture, so it starts in `requires_confirmation` with nothing capturable or received.
- `status` prints the same line.
- `confirm` authorizes the full amount: the intent moves to `requires_capture` with `amount_capturable=5000`.
- `capture` collects the authorized 5000: `succeeded`, `amount_capturable=0`, `amount_received=5000`.
- `cancel` is not allowed on a `succeeded` intent: `ERR_INVALID_STATE`.
- `pi_1002` is created with its parameters in a different order. It has no `capture_method`, so it is `automatic`.
- Confirming an automatic intent collects the money at once: `succeeded` with `amount_received=1250`.
- `status` shows the same line.

## Sample Case 1

### Sample Input For Custom Testing

```
11
1700000000|create|pi=pi_A;amount=0;currency=usd
1700000001|create|pi=pi_A;amount=700;currency=USD
1700000002|create|pi=pi_A;amount=700;currency=usd
1700000003|create|pi=pi_A;amount=900;currency=gbp
1700000004|capture|pi=pi_A
1700000005|confirm|pi=pi_B
1700000006|confirm|pi=pi_A;pi=pi_A
1700000007|void|pi=pi_A
1700000008|cancel|pi=pi_A
1700000009|confirm|pi=pi_A
1700000010|status
```

### Sample Output

```
ERR_INVALID_PARAM
ERR_INVALID_PARAM
pi_A requires_confirmation usd amount=700 amount_capturable=0 amount_received=0
ERR_DUPLICATE
ERR_INVALID_STATE
ERR_NOT_FOUND
ERR_MALFORMED
ERR_MALFORMED
pi_A canceled usd amount=700 amount_capturable=0 amount_received=0
ERR_INVALID_STATE
ERR_MALFORMED
```

### Explanation

- An amount of `0` is out of range: `ERR_INVALID_PARAM`.
- `USD` is not lowercase: `ERR_INVALID_PARAM`. Neither of these two commands created anything.
- The third command creates `pi_A` (automatic capture).
- Creating `pi_A` again fails with `ERR_DUPLICATE`, even though the amount and currency differ.
- `capture` needs `requires_capture`, but `pi_A` is in `requires_confirmation`: `ERR_INVALID_STATE`.
- `pi_B` does not exist: `ERR_NOT_FOUND`.
- The key `pi` appears twice: `ERR_MALFORMED`.
- `void` is not an action: `ERR_MALFORMED`.
- `cancel` is allowed from `requires_confirmation`, so `pi_A` becomes `canceled`.
- A canceled intent cannot be confirmed: `ERR_INVALID_STATE`.
- `1700000010|status` has only two fields: `ERR_MALFORMED`.
