# Merchant Ledger: Part 1

You are building the core of a ledger that tracks money held by merchants on a payments platform. Each merchant has one **account**, identified by an account id, that holds a balance in US dollars. A balance is always an exact number of cents and can never go below zero.

Merchants add money to their accounts with deposits and move money to each other with payments. Every successful payment receives a payment id. Payment ids are `pay_1`, `pay_2`, `pay_3`, ... assigned in the order the payments succeed, starting at `pay_1`. A command that fails never uses up a payment id.

Your program receives a chronological list of commands and must produce exactly one output line per command: either the result of the command or an error token. A command that fails has no effect on the ledger.

## Commands

Each command is a single string made of tokens separated by exactly one space character, with no leading or trailing spaces:

`<timestamp> <COMMAND> <arg1> <arg2> ...`

`<timestamp>` is a positive integer. Timestamps are non-decreasing from one command to the next, and several commands may share a timestamp. In this part timestamps have no effect on the result. `<COMMAND>` is the command name, matched exactly and case sensitively (`DEPOSIT` is a command, `deposit` and `Deposit` are not). All other tokens are the command's arguments.

| Command | Format | Output |
|---|---|---|
| Create account | `<timestamp> CREATE_ACCOUNT <account>` | `OK` |
| Deposit | `<timestamp> DEPOSIT <account> <amount>` | the account's new balance |
| Pay | `<timestamp> PAY <from> <to> <amount>` | the new payment id, for example `pay_1` |
| Balance | `<timestamp> BALANCE <account>` | the account's current balance |

### Account ids

A **valid account id** is 1 to 20 characters long, starts with a lowercase letter `a` to `z`, and contains only lowercase letters `a` to `z`, digits `0` to `9` and underscores `_`. Account ids are case sensitive. Only `CREATE_ACCOUNT` checks the format of an account id. Every other command looks the id up exactly as written, so an id that is malformed or was never created is simply an account that does not exist.

### Amounts

Money amounts are written as decimal strings. An amount token is **valid** only if all of the following hold:

1. It consists of an integer part, optionally followed by a single `.` and a fractional part.
2. The integer part is one or more digits `0` to `9`. It must not start with `0` unless it is exactly `0` (so `0.50` is allowed, `00.50` and `05` are not).
3. If a `.` is present, the fractional part is exactly 1 or 2 digits (`5.5` means 5 dollars 50 cents; `5.` and `5.123` are invalid).
4. No other characters are allowed: no sign (`+5` and `-5` are invalid), no leading `.` (`.5` is invalid), no thousands separators, no exponent, no currency symbol.
5. Its value is greater than zero and at most `1000000.00` (so `0`, `0.0` and `0.00` are invalid, `1000000` is valid and `1000000.01` is invalid).

Valid examples: `12`, `12.5`, `12.50`, `0.01`, `1000000.00`.

### Output format for money

Every balance or amount that your program prints is written as the whole number of dollars (no leading zeros, `0` when below one dollar), a `.`, and exactly two digits of cents. Examples: `0.00`, `0.05`, `7.50`, `1000000.00`. No sign, no thousands separators. Amounts are exact cent values, so no rounding ever happens.

### Command rules

**CREATE_ACCOUNT `<account>`** creates a new account with balance `0.00` and outputs `OK`. Checks, in order:
1. Exactly 1 argument, and it is a valid account id. Otherwise `ERROR_INVALID_ARGS`.
2. No account with this id has been created before. Otherwise `ERROR_ACCOUNT_EXISTS`.

**DEPOSIT `<account> <amount>`** adds the amount to the account and outputs the new balance. Checks, in order:
1. Exactly 2 arguments. Otherwise `ERROR_INVALID_ARGS`.
2. The amount is valid. Otherwise `ERROR_INVALID_AMOUNT`.
3. The account exists. Otherwise `ERROR_ACCOUNT_NOT_FOUND`.

**PAY `<from> <to> <amount>`** moves the amount from account `<from>` to account `<to>`, records it as a new payment and outputs its payment id. Checks, in order:
1. Exactly 3 arguments. Otherwise `ERROR_INVALID_ARGS`.
2. The amount is valid. Otherwise `ERROR_INVALID_AMOUNT`.
3. Both accounts exist. Otherwise `ERROR_ACCOUNT_NOT_FOUND`.
4. `<from>` and `<to>` are different accounts. Otherwise `ERROR_SAME_ACCOUNT`.
5. The balance of `<from>` is greater than or equal to the amount. Otherwise `ERROR_INSUFFICIENT_FUNDS`. Paying exactly the full balance is allowed and leaves `0.00`.

**BALANCE `<account>`** outputs the account's current balance. Checks, in order:
1. Exactly 1 argument. Otherwise `ERROR_INVALID_ARGS`.
2. The account exists. Otherwise `ERROR_ACCOUNT_NOT_FOUND`.

### Invalid commands

Every command produces exactly one output line. A command is processed as follows, and the first failing check decides the output:

1. If `<COMMAND>` is not one of the command names above (exact, case sensitive match), output `ERROR_UNKNOWN_COMMAND`, regardless of its arguments.
2. Otherwise apply that command's checks in the order listed above. "Exactly N arguments" counts the tokens after the command name.

The complete list of error tokens in this part is: `ERROR_UNKNOWN_COMMAND`, `ERROR_INVALID_ARGS`, `ERROR_INVALID_AMOUNT`, `ERROR_ACCOUNT_EXISTS`, `ERROR_ACCOUNT_NOT_FOUND`, `ERROR_SAME_ACCOUNT`, `ERROR_INSUFFICIENT_FUNDS`. A command that outputs an error token changes nothing.

## Function Description

Complete the function `processLedger` in the editor below.

`processLedger` has the following parameter:

- `string commands[n]`: the commands, in chronological order

Returns:

- `string[]`: exactly `n` lines, where line `i` is the output of `commands[i]`

## Constraints

- `1 ≤ n ≤ 10^4`
- Each command has at least two tokens: a timestamp and a command name. Tokens are separated by exactly one space.
- Each timestamp is an integer written without leading zeros, `1 ≤ timestamp ≤ 10^9`, and timestamps are non-decreasing.
- Every token is a non-empty string of printable ASCII characters (no spaces) of length at most 25.

## Input Format For Custom Testing

The first line contains an integer, `n`, the number of commands.
Each of the next `n` lines contains a string, `commands[i]`.

## Sample Case 0

### Sample Input For Custom Testing

```
8
1 CREATE_ACCOUNT acme
2 CREATE_ACCOUNT globex
3 DEPOSIT acme 100.50
4 PAY acme globex 40.25
5 BALANCE acme
6 BALANCE globex
7 PAY globex acme 50
8 CREATE_ACCOUNT acme
```

### Sample Output

```
OK
OK
100.50
pay_1
60.25
40.25
ERROR_INSUFFICIENT_FUNDS
ERROR_ACCOUNT_EXISTS
```

### Explanation

- `CREATE_ACCOUNT acme` and `CREATE_ACCOUNT globex` create two accounts with balance `0.00`. Each outputs `OK`.
- `DEPOSIT acme 100.50` brings `acme` to `100.50`.
- `PAY acme globex 40.25` succeeds. It is the first successful payment, so it outputs `pay_1`.
- `BALANCE acme` is `100.50 - 40.25 = 60.25`. `BALANCE globex` is `40.25`.
- `PAY globex acme 50` fails because `globex` holds only `40.25`, so it outputs `ERROR_INSUFFICIENT_FUNDS`.
- `CREATE_ACCOUNT acme` fails with `ERROR_ACCOUNT_EXISTS`.

## Sample Case 1

### Sample Input For Custom Testing

```
9
1 CREATE_ACCOUNT shop_1
2 DEPOSIT shop_1 12.5
3 DEPOSIT shop_1 1.999
4 DEPOSIT shop_1 +3
5 DEPOSIT ghost 5
6 PAY shop_1 shop_1 1
7 Deposit shop_1 5
8 BALANCE shop_1 extra
9 BALANCE shop_1
```

### Sample Output

```
OK
12.50
ERROR_INVALID_AMOUNT
ERROR_INVALID_AMOUNT
ERROR_ACCOUNT_NOT_FOUND
ERROR_SAME_ACCOUNT
ERROR_UNKNOWN_COMMAND
ERROR_INVALID_ARGS
12.50
```

### Explanation

- `CREATE_ACCOUNT shop_1` outputs `OK` (underscores and digits are allowed after the first letter).
- `DEPOSIT shop_1 12.5` deposits 12 dollars 50 cents, printed as `12.50`.
- `1.999` has three fractional digits and `+3` has a sign, so both deposits output `ERROR_INVALID_AMOUNT`.
- `DEPOSIT ghost 5` has a valid amount but `ghost` does not exist: `ERROR_ACCOUNT_NOT_FOUND`.
- `PAY shop_1 shop_1 1` pays an account to itself: `ERROR_SAME_ACCOUNT`.
- `Deposit` is not a command name (names are case sensitive): `ERROR_UNKNOWN_COMMAND`.
- `BALANCE shop_1 extra` has 2 arguments instead of 1: `ERROR_INVALID_ARGS`.
- `BALANCE shop_1` is still `12.50`, because none of the failed commands changed anything.
