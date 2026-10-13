# API Gateway Rate Limiter: Part 1

You are building the rate limiter that sits in the API gateway in front of a payments API. Every call a merchant makes (create a charge, refund a payment, look up a customer) passes through the gateway first. The gateway decides whether to forward the call (`ALLOW`) or reject it with HTTP 429 (`DENY`) so that a single integration cannot overload the API.

Each request is made with an **API key**. An API key starts existing the first time it appears in a valid command; there is no registration step. In this part every API key has the same limit: **at most 3 counted requests in each 10-second window**. Windows are fixed and aligned to timestamp 0: window `k` covers the timestamps `t` with `10k ≤ t < 10(k+1)`, so `[0, 10)`, `[10, 20)`, `[20, 30)` and so on. The start of a window is inside it and the end is not: a request at `t = 10` belongs to window `[10, 20)`. Each API key has its own counter, and a new window starts with a counter of 0 for every key.

Requests to the health check endpoint `/v1/health` are exempt: they are always allowed and are never counted. The gateway compares paths only after normalizing them (see below).

You receive the gateway's log of commands in chronological order and must output the gateway's decision for each one.

## Commands

Each command is a single string made of fields separated by exactly one space. There are no leading or trailing spaces. The first field is always the timestamp and the second field is the command name.

| Command | Format | Output |
|---|---|---|
| Request | `<timestamp> REQUEST <api_key> <method> <path>` | `ALLOW`, `DENY global_limit` or `INVALID` |

Every command produces exactly one output line.

### Field formats

- **Integer fields.** Wherever this problem asks for an integer, the field must be a non-empty string made only of the ASCII digits `0` to `9`. Signs, decimal points, exponents, underscores, hexadecimal prefixes and any other characters make the field malformed. Leading zeros are allowed and ignored: `007` is the integer 7.
- **`timestamp`**: an integer, in seconds.
- **Command names** are case sensitive: `REQUEST` is a command, `request` and `Request` are not.
- **`api_key`**: the prefix `sk_live_` or `sk_test_` followed by 1 to 24 characters, each an ASCII letter (`a` to `z`, `A` to `Z`) or a digit (`0` to `9`). API keys are case sensitive and are compared as whole strings: `sk_test_abc`, `sk_test_ABC` and `sk_live_abc` are three different keys.
- **`method`**: exactly one of `GET`, `POST`, `DELETE` (case sensitive).
- **`path`**: any string that starts with `/`. It never contains a space.

### Path normalization

Before a path is used for any decision, it is normalized by these steps, in this order:

1. If the path contains `?`, remove the first `?` and everything after it (the query string).
2. Replace every run of two or more consecutive `/` characters with a single `/`.
3. If the result is longer than one character and ends with `/`, remove that final `/`.

Examples: `/v1//charges/?limit=3` becomes `/v1/charges`; `//` becomes `/`; `/?a=b` becomes `/`. Paths are case sensitive, and no other character has a special meaning (for example `#` is an ordinary character). Normalization never makes a path invalid.

### REQUEST

`<timestamp> REQUEST <api_key> <method> <path>`

A valid request is processed as follows:

1. If the normalized path is exactly `/v1/health`, output `ALLOW`. The request is not counted. The method does not matter.
2. Otherwise, if the key has already made 3 counted requests in the window that contains `timestamp`, output `DENY global_limit`. A denied request is not counted.
3. Otherwise output `ALLOW` and count the request against the key in the current window.

The method does not affect the decision in this part, but it must be valid.

### Invalid commands

A command outputs `INVALID`, and has no other effect (nothing is counted), when any of the following holds:

- the first field is not an integer;
- there is no second field, or the second field is not a known command name;
- a `REQUEST` does not have exactly 5 fields;
- the `api_key`, `method` or `path` does not match its format above.

## Function Description

Complete the function `rateLimiter` in the editor below.

`rateLimiter` has the following parameter:

- `string commands[n]`: the commands, in chronological order

Returns:

- `string[]`: exactly one output line per command, in the same order as the commands

## Constraints

- `1 ≤ n ≤ 10^4`
- Each command has between 1 and 200 characters, all printable ASCII.
- Every timestamp that is an integer satisfies `0 ≤ timestamp ≤ 10^9`, and these timestamps are non-decreasing in command order. Several commands may share a timestamp; they are processed in the order given.

## Input Format For Custom Testing

The first line contains an integer, `n`, the number of commands.
Each of the next `n` lines contains a string, `commands[i]`.

## Sample Case 0

### Sample Input For Custom Testing

```
7
1 REQUEST sk_test_alice POST /v1/charges
2 REQUEST sk_test_alice GET /v1/charges/ch_1
4 REQUEST sk_test_alice POST /v1/refunds
5 REQUEST sk_test_alice POST /v1/charges
6 REQUEST sk_live_bob POST /v1/charges
9 REQUEST sk_test_alice GET /v1/customers
10 REQUEST sk_test_alice GET /v1/customers
```

### Sample Output

```
ALLOW
ALLOW
ALLOW
DENY global_limit
ALLOW
DENY global_limit
ALLOW
```

### Explanation

- `t=1`, `t=2`, `t=4`: the first three requests of `sk_test_alice` in window `[0, 10)` are allowed and counted. The method and path do not matter.
- `t=5`: `sk_test_alice` already has 3 counted requests in `[0, 10)`, so `DENY global_limit`.
- `t=6`: `sk_live_bob` has its own counter, which is 0, so `ALLOW`.
- `t=9`: still window `[0, 10)` for `sk_test_alice`, so `DENY global_limit`.
- `t=10`: a new window `[10, 20)` starts at 10 (the end of a window is not inside it), so `ALLOW`.

## Sample Case 1

### Sample Input For Custom Testing

```
11
0 REQUEST sk_test_alice GET /v1//health/?verbose=1
0 REQUEST sk_test_alice GET /v1/health
1 REQUEST sk_test_alice POST /v1/charges
1 REQUEST sk_test_alice POST /v1/charges?expand=customer
2 REQUEST sk_test_alice POST /v1/charges
3 REQUEST sk_test_alice GET /V1/Health
3 REQUEST sk_test_alice PATCH /v1/charges
x REQUEST sk_test_alice GET /v1/charges
4 REQUEST pk_test_alice GET /v1/charges
5 REQUEST sk_test_alice GET v1/charges
6 REFUND sk_test_alice
```

### Sample Output

```
ALLOW
ALLOW
ALLOW
ALLOW
ALLOW
DENY global_limit
INVALID
INVALID
INVALID
INVALID
INVALID
```

### Explanation

- `/v1//health/?verbose=1` normalizes to `/v1/health` (query removed, `//` collapsed, trailing `/` removed), so it is exempt: `ALLOW`, not counted. The plain `/v1/health` at `t=0` is exempt too.
- `t=1`, `t=1`, `t=2`: three counted requests (`/v1/charges?expand=customer` normalizes to `/v1/charges`), all allowed.
- `t=3` `/V1/Health`: paths are case sensitive, so this is not the health endpoint. The key already has 3 counted requests in `[0, 10)`: `DENY global_limit`.
- `PATCH` is not a valid method: `INVALID`.
- `x` is not an integer timestamp: `INVALID`.
- `pk_test_alice` does not start with `sk_live_` or `sk_test_`: `INVALID`.
- `v1/charges` does not start with `/`: `INVALID`.
- `REFUND` is not a known command: `INVALID`.
