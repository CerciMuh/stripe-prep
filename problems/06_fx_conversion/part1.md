# FX Conversion Service: Part 1

You are building the currency conversion service that sits behind a payments platform. When a merchant in one country charges a customer in another, the platform converts the amount using exchange rates published by the treasury team. Your service receives a chronological stream of commands: some publish exchange rates, and some ask for an amount to be converted.

A **currency** is identified by a code of exactly 3 uppercase ASCII letters (`A` to `Z`), for example `USD`. Any such code is a valid currency, even if it is not a real one. Each currency has a fixed number of **minor units** (decimal places):

| Minor units | Currencies |
|---|---|
| 0 | `CLP`, `ISK`, `JPY`, `KRW`, `VND` |
| 3 | `BHD`, `JOD`, `KWD`, `OMR`, `TND` |
| 2 | every other currency |

A **rate** for the ordered pair `(FROM, TO)` means that 1 unit of `FROM` is worth `rate` units of `TO`. Rates are stored per direction: a rate for `(USD, EUR)` and a rate for `(EUR, USD)` are two independent values. If the service only knows the rate for one direction, the opposite direction is **implied**: converting from `TO` back to `FROM` divides by the known rate.

All amounts and rates are exact decimal numbers. Never use binary floating point. Intermediate values are never rounded. Only the final converted amount is rounded, once, using **round half up** (a remainder of exactly one half rounds away from zero) to the minor units of the target currency. Tests are constructed so that evaluating each conversion with exact decimal arithmetic, or with at least 28 significant digits of precision, gives the same final result.

## Commands

Each command is a single string made of fields separated by commas (`,`). Fields are never trimmed: a field that contains a space is malformed. Command names and currency codes are case sensitive.

| Command | Format | Output |
|---|---|---|
| Set rate | `RATE,<FROM>,<TO>,<rate>` | `OK` |
| Convert | `CONVERT,<amount>,<FROM>,<TO>` | the converted amount, or `NO_RATE` |

Every command produces exactly one output line. An invalid command produces `INVALID` (see below).

### Number formats

- A **rate** is one or more ASCII digits `0` to `9`, optionally followed by a `.` and between 1 and 6 digits. Its value must be strictly greater than zero. Leading zeros are allowed (`00.5` is the rate 0.5). Examples of malformed rates: `1.`, `.5`, `-1`, `+1`, `1e3`, `1.1234567` (7 decimals), `0`, `0.000`.
- An **amount** is one or more ASCII digits, optionally followed by a `.` and one or more digits. The number of digits after the `.` must not exceed the minor units of the `FROM` currency, so a currency with 0 minor units does not allow a `.` at all (`100.0` is malformed for `JPY`). Trailing zeros count: `10.120` has 3 digits after the `.` and is malformed for `EUR`. The value must be strictly greater than zero. Leading zeros are allowed.

### RATE

`RATE,<FROM>,<TO>,<rate>` sets the rate for the direction `FROM` to `TO`, replacing any rate previously set for that same direction. It does not change the rate stored for the opposite direction. Output `OK`.

### CONVERT

`CONVERT,<amount>,<FROM>,<TO>` converts `amount` units of `FROM` into `TO`:

1. If a rate was set for the direction `(FROM, TO)`, the result is `amount × rate`.
2. Otherwise, if a rate was set for the opposite direction `(TO, FROM)`, the result is `amount ÷ rate` (the implied inverse).
3. Otherwise the output is `NO_RATE`.

A rate set explicitly for a direction always takes precedence over the implied inverse of the opposite direction. `CONVERT` only uses a rate between `FROM` and `TO` themselves. It never chains through a third currency.

The result is rounded half up to the minor units of `TO` and printed with exactly that many digits after the decimal point. Print a `.` only when `TO` has more than 0 minor units, always print at least one digit before the `.`, and never use a thousands separator, a sign or exponent notation. For example `114.63` (EUR), `2995` (JPY), `0.004` (KWD). A result that rounds to zero is printed as zero (`0.00`), it is not an error.

### Invalid commands

A command is `INVALID` if any of the following holds. An invalid command changes no state.

- The command name is not exactly `RATE` or `CONVERT` (for example `rate`, `Rate` or `QUOTE`).
- The number of fields is wrong: `RATE` and `CONVERT` each take exactly 4 fields including the name. Empty fields count as fields (a trailing comma adds an empty field).
- A currency code is not exactly 3 uppercase letters `A` to `Z`.
- `FROM` and `TO` are the same currency.
- The rate or the amount is malformed or not strictly positive, as defined above.

Validity is checked before rates are looked up, so `NO_RATE` is only produced for a well formed `CONVERT`.

## Function Description

Complete the function `processFxCommands` in the editor below.

`processFxCommands` has the following parameter:

- `string commands[n]`: the commands, in chronological order

Returns:

- `string[]`: exactly `n` lines, where line `i` is the output of `commands[i]`

## Constraints

- `1 ≤ n ≤ 10^4`
- Each command is at most 100 characters long, contains no newline, and has no trailing whitespace.
- Valid rates are at most `10^6`. Valid amounts are at most `10^9`. These bounds are guarantees about the tests, not validation rules.
- Every converted amount, including every intermediate amount along a route, is less than `10^15`.
- At most 30 distinct currency codes appear in valid commands.

## Input Format For Custom Testing

The first line contains an integer, `n`, the number of commands.
Each of the next `n` lines contains a string, `commands[i]`.

## Sample Case 0

### Sample Input For Custom Testing

```
9
RATE,USD,EUR,0.9134
CONVERT,125.50,USD,EUR
CONVERT,100,EUR,USD
RATE,EUR,USD,1.0950
CONVERT,100,EUR,USD
CONVERT,10,USD,GBP
RATE,USD,JPY,149.82
CONVERT,19.99,USD,JPY
CONVERT,2995,JPY,USD
```

### Sample Output

```
OK
114.63
109.48
OK
109.50
NO_RATE
OK
2995
19.99
```

### Explanation

- `RATE,USD,EUR,0.9134` stores 1 USD = 0.9134 EUR. Output `OK`.
- `CONVERT,125.50,USD,EUR`: 125.50 × 0.9134 = 114.6317, rounded half up to 2 places is `114.63`.
- `CONVERT,100,EUR,USD`: no rate is set for EUR to USD, so the inverse of the USD to EUR rate is implied: 100 ÷ 0.9134 = 109.4810..., which gives `109.48`.
- `RATE,EUR,USD,1.0950` sets the EUR to USD direction explicitly. Output `OK`.
- `CONVERT,100,EUR,USD`: the explicit rate now takes precedence over the implied inverse: 100 × 1.0950 = `109.50`.
- `CONVERT,10,USD,GBP`: no rate exists in either direction between USD and GBP, so the output is `NO_RATE`.
- `RATE,USD,JPY,149.82`: output `OK`.
- `CONVERT,19.99,USD,JPY`: 19.99 × 149.82 = 2994.9018. JPY has 0 minor units, so the result is `2995`.
- `CONVERT,2995,JPY,USD`: implied inverse, 2995 ÷ 149.82 = 19.9906..., which gives `19.99`.

## Sample Case 1

### Sample Input For Custom Testing

```
11
RATE,GBP,KWD,0.3871
CONVERT,1000,GBP,KWD
CONVERT,1.005,KWD,GBP
CONVERT,12.345,GBP,KWD
RATE,usd,EUR,0.9
RATE,USD,USD,1
RATE,EUR,CHF,0
CONVERT,-5,GBP,KWD
CONVERT,0.00,GBP,KWD
SWAP,GBP,KWD
CONVERT,0.01,GBP,KWD
```

### Sample Output

```
OK
387.100
2.60
INVALID
INVALID
INVALID
INVALID
INVALID
INVALID
INVALID
0.004
```

### Explanation

- `RATE,GBP,KWD,0.3871`: output `OK`.
- `CONVERT,1000,GBP,KWD`: 1000 × 0.3871 = 387.1. KWD has 3 minor units, so it prints as `387.100`.
- `CONVERT,1.005,KWD,GBP`: the amount has 3 decimals, which KWD allows. Implied inverse: 1.005 ÷ 0.3871 = 2.5962..., which gives `2.60`.
- `CONVERT,12.345,GBP,KWD`: GBP has 2 minor units, so an amount with 3 decimals is `INVALID`.
- `RATE,usd,EUR,0.9`: `usd` is not uppercase. `INVALID`.
- `RATE,USD,USD,1`: same currency on both sides. `INVALID`.
- `RATE,EUR,CHF,0`: a rate must be strictly positive. `INVALID`.
- `CONVERT,-5,GBP,KWD`: a sign is not allowed. `INVALID`.
- `CONVERT,0.00,GBP,KWD`: an amount must be strictly positive. `INVALID`.
- `SWAP,GBP,KWD`: unknown command. `INVALID`.
- `CONVERT,0.01,GBP,KWD`: 0.01 × 0.3871 = 0.003871, which rounds half up to 3 places as `0.004`.
