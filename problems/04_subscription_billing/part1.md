# Subscription Billing: Part 1

You are building the core of a subscription billing engine. Merchants define **plans** with a monthly price, customers **subscribe** to a plan, and the engine issues an **invoice** at the start of every monthly billing period until the subscription is canceled. Your program receives a chronological list of commands and must report the invoices the engine produces.

Every command carries a calendar date. The engine has a clock that only moves forward. Before a command dated `D` is processed, the engine first performs all scheduled billing work dated on or before `D` that has not been performed yet (renewals and cancellations taking effect, described below). Only then is the command itself checked and applied. Work that is due on the same date as a command therefore always happens before that command.

A subscription belongs to one customer and is either **live** or **ended**. A customer can have at most one live subscription at a time. When a subscription is created on date `S`, `S` becomes its **anchor date**. Its billing periods are monthly and always computed from the anchor: the `k`-th period boundary is the date `k` calendar months after the anchor, keeping the anchor's day of month, or using the last day of that month if the month is too short. Boundaries are always computed from the anchor, never from the previous boundary. For example, an anchor of `2024-01-31` gives boundaries `2024-02-29`, `2024-03-31`, `2024-04-30`, `2024-05-31`, and so on. A billing period runs from its start date up to, but not including, its end date (the next boundary).

On each boundary date, a live subscription either renews (a new period starts and a new invoice is issued) or, if a cancellation is pending, ends.

## Commands

Each command is a single string of comma separated fields. The first field is always the date, in the form `YYYY-MM-DD`. The second field is the command name. Command names and ids are case sensitive.

| Command | Format | Output |
|---|---|---|
| Define a plan | `DATE,PLAN,plan_id,price` | nothing, or `INVALID` |
| Subscribe | `DATE,SUBSCRIBE,customer_id,plan_id` | nothing, or `INVALID` |
| Cancel | `DATE,CANCEL,customer_id` | nothing, or `INVALID` |
| Invoice run | `DATE,ADVANCE` | one line per invoice, or `NO_INVOICES`, or `INVALID` |

**Dates.** A date field is valid only if it is exactly 10 characters of the form `YYYY-MM-DD` (4 digit year, 2 digit month, 2 digit day, each digit `0` to `9`, separated by `-`) and names a real day of the Gregorian calendar. `2024-02-29` is valid; `2023-02-29`, `2100-02-29`, `2024-04-31`, `2024-13-01`, `2024-1-05` and `20240105` are not. A year is a leap year if it is divisible by 4, except years divisible by 100 that are not divisible by 400.

**PLAN.** Creates plan `plan_id` with monthly price `price`, in cents. `price` must consist only of the digits `0` to `9` (no sign, no decimal point, no other characters; leading zeros are allowed, so `0500` is 500) and its value must be between `1` and `10000000` inclusive. Plans can never be changed, and a plan id can only be defined once.

**SUBSCRIBE.** Creates a new subscription for `customer_id` on plan `plan_id`, anchored at the command date `D`. The customer does not need to exist before; customers are identified only by their id. The first period starts at `D`, and an invoice for it is issued immediately. A customer whose previous subscription has ended may subscribe again; the new subscription has its own anchor.

**CANCEL.** Schedules the customer's live subscription to end at the end of its current period. No invoice is issued at that boundary. On that date the subscription ends, so a `SUBSCRIBE` for the same customer dated on or after that boundary is accepted.

**ADVANCE.** Prints every invoice issued since the previous valid `ADVANCE` (or since the start), one per line, in the order they were issued. If there are none, it prints the single line `NO_INVOICES`. Invoices issued by commands or work dated on the `ADVANCE` date itself are included, since they happen before the `ADVANCE` is processed.

**Invoices.** Invoices are numbered with one global counter in the order they are issued: `in_1`, `in_2`, and so on. There are two kinds:

- `CREATE`: issued by a `SUBSCRIBE` for the first period.
- `CYCLE`: issued on a boundary date when a subscription renews.

Each invoice is printed as

`invoice_id,customer_id,plan_id,reason,period_start,period_end,amount`

where `reason` is `CREATE` or `CYCLE`, the dates are in `YYYY-MM-DD` form, and `amount` is the plan price in cents, as an integer without leading zeros.

**Order of scheduled work.** When the clock moves forward, scheduled work is performed date by date in increasing order. On one date, customers are handled in ascending order of customer id, comparing ids character by character by ASCII code (so `Zed` comes before `alpha`, and `cus_10` comes before `cus_2`). A subscription may renew several times in one jump of the clock; each renewal issues its own invoice.

### Invalid commands

A command is invalid, prints the single line `INVALID` and has no effect if any of the following holds:

- The date field is not a valid date, or the command has fewer than 2 fields.
- The command name is not one of the names in the table above (names are case sensitive, so `subscribe` is invalid).
- The number of fields is not exactly the number shown in the table for that command.
- An id field (`plan_id`, `customer_id`) is empty.
- `PLAN`: `price` is not a valid price as defined above, or `plan_id` already exists.
- `SUBSCRIBE`: `plan_id` does not exist, or the customer already has a live subscription.
- `CANCEL`: the customer has no live subscription, or a cancellation is already pending for it.

Valid `PLAN`, `SUBSCRIBE` and `CANCEL` commands print nothing.

## Function Description

Complete the function `processBilling` in the editor below.

`processBilling` has the following parameter:

- `string commands[n]`: the commands, in chronological order

Returns:

- `string[]`: the output lines of all commands, in order: one `INVALID` line for each invalid command, and the lines printed by each valid `ADVANCE`

## Constraints

- `1 ≤ n ≤ 10^4`
- Commands contain only printable ASCII characters and no whitespace.
- Every command whose date field is a valid date has a date no earlier than any previous command with a valid date.
- All valid dates are between `2000-01-01` and `2100-12-31`.
- Non-empty ids consist of letters, digits and underscores, at most 20 characters.

## Input Format For Custom Testing

The first line contains an integer, `n`, the number of commands.
Each of the next `n` lines contains a string, `commands[i]`.

## Sample Case 0

### Sample Input For Custom Testing

```
8
2024-01-01,PLAN,plan_basic,1000
2024-01-31,PLAN,plan_pro,2999
2024-01-31,SUBSCRIBE,cus_1,plan_pro
2024-01-31,ADVANCE
2023-02-29,PLAN,plan_x,500
2024-02-15,SUBSCRIBE,cus_2,plan_basic
2024-03-31,ADVANCE
2024-04-01,ADVANCE
```

### Sample Output

```
in_1,cus_1,plan_pro,CREATE,2024-01-31,2024-02-29,2999
INVALID
in_2,cus_2,plan_basic,CREATE,2024-02-15,2024-03-15,1000
in_3,cus_1,plan_pro,CYCLE,2024-02-29,2024-03-31,2999
in_4,cus_2,plan_basic,CYCLE,2024-03-15,2024-04-15,1000
in_5,cus_1,plan_pro,CYCLE,2024-03-31,2024-04-30,2999
NO_INVOICES
```

### Explanation

- Plans `plan_basic` (1000 cents) and `plan_pro` (2999 cents) are defined.
- `cus_1` subscribes to `plan_pro` on `2024-01-31`. The anchor day is 31. Invoice `in_1` covers `2024-01-31` up to `2024-02-29`, because February 2024 has only 29 days.
- The first `ADVANCE` prints `in_1`.
- `2023-02-29` is not a real date (2023 is not a leap year), so that command prints `INVALID`.
- `cus_2` subscribes to `plan_basic` on `2024-02-15` and gets `in_2`.
- Before the `ADVANCE` dated `2024-03-31` runs, the clock moves through `2024-02-29` (`cus_1` renews, `in_3`), `2024-03-15` (`cus_2` renews, `in_4`) and `2024-03-31` (`cus_1` renews, `in_5`). The anchor day 31 is kept, so after `2024-02-29` the next boundary is `2024-03-31`, then `2024-04-30`.
- Nothing new is issued by `2024-04-01`, so the last `ADVANCE` prints `NO_INVOICES`.

## Sample Case 1

### Sample Input For Custom Testing

```
10
2024-03-01,PLAN,plan_team,5000
2024-03-01,SUBSCRIBE,acme,plan_team
2024-03-10,SUBSCRIBE,acme,plan_team
2024-03-10,CANCEL,acme
2024-03-20,CANCEL,acme
2024-04-01,SUBSCRIBE,acme,plan_team
2024-04-01,PLAN,plan_team,6000
2024-04-02,subscribe,bob,plan_team
2024-04-05,PLAN,plan_solo,+900
2024-05-01,ADVANCE
```

### Sample Output

```
INVALID
INVALID
INVALID
INVALID
INVALID
in_1,acme,plan_team,CREATE,2024-03-01,2024-04-01,5000
in_2,acme,plan_team,CREATE,2024-04-01,2024-05-01,5000
in_3,acme,plan_team,CYCLE,2024-05-01,2024-06-01,5000
```

### Explanation

- `acme` subscribes to `plan_team` on `2024-03-01`, issuing `in_1` for `2024-03-01` up to `2024-04-01`.
- On `2024-03-10`, `acme` already has a live subscription, so the second `SUBSCRIBE` is `INVALID`. The `CANCEL` on the same day is accepted: the subscription will end on `2024-04-01`.
- The `CANCEL` on `2024-03-20` is `INVALID` because a cancellation is already pending.
- On `2024-04-01`, the scheduled work runs first: the subscription ends without an invoice. The `SUBSCRIBE` on that date is then accepted and issues `in_2` with a new anchor `2024-04-01`.
- Redefining `plan_team` is `INVALID`, `subscribe` is not a known command name, and `+900` is not a valid price, so those three commands print `INVALID`.
- On `2024-05-01`, the new subscription renews (`in_3`) before the `ADVANCE`, which prints `in_1`, `in_2` and `in_3`.
