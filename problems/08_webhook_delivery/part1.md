# Webhook Delivery: Part 1

Stripe tells merchants about activity on their account by sending **events** to HTTPS **endpoints** that the merchant registers. Each endpoint subscribes to the event types it cares about using patterns such as `charge.*` or `invoice.paid`. When an event is emitted, every endpoint whose subscription matches it gets its own **delivery** of that event.

You are building a simulator for the webhook dispatcher. Nothing touches the network: the response that each endpoint gives is configured with a command. The simulator has a **clock** that starts at `0` and only changes when a `TICK` command is processed. Deliveries are not sent the moment an event is emitted. Each delivery is **scheduled** at the clock value at the moment its event was emitted, and it is only attempted when a `TICK` command runs the dispatcher.

Every endpoint has an id, a list of patterns, and a **configured response**. The configured response starts as `200` and can be changed with `SET_STATUS`. An attempt is a **success** if the configured response is a status code from `200` to `299` inclusive. Any other status code, and `timeout`, is a **failure**. In this part every delivery is attempted exactly once: after its attempt the delivery is finished, whether it succeeded or failed.

## Commands

Each command is a single string. Fields are separated by a single space character. Split the command on every space: if any field is empty (because of a leading space or two consecutive spaces), the command is invalid. The first field is the command name. Command names, ids, event types and every other token are case sensitive.

| Command | Format | Output |
|---|---|---|
| Register endpoint | `REGISTER <endpoint_id> <patterns>` | nothing, or `INVALID` |
| Set response | `SET_STATUS <endpoint_id> <response>` | nothing, or `INVALID` |
| Emit event | `EMIT <event_id> <event_type>` | nothing, or `INVALID` |
| Advance clock | `TICK <timestamp>` | one line per delivery attempt (possibly none), or `INVALID` |

### Token formats

- `<endpoint_id>`: the characters `we_` followed by one or more characters, each a lowercase letter `a` to `z` or a digit `0` to `9`. For example `we_a`, `we_10`, `we_shop7`. (`we_`, `WE_a`, `we_A` and `we_a_b` are malformed.)
- `<event_id>`: the characters `evt_` followed by one or more lowercase letters or digits. For example `evt_1`, `evt_9ab`.
- `<event_type>`: one or more **segments** joined by `.`. A segment is one or more characters, each a lowercase letter, a digit or `_`. For example `charge`, `invoice.paid`, `customer.subscription.updated`.
- A **pattern** is either the single character `*`, or one or more segments joined by `.` where each segment is either exactly `*` or a valid event type segment. For example `charge.*`, `*.created`, `customer.*.updated`, `*.*`. (`charge*`, `**`, `charge.` and `CHARGE.*` are malformed.)
- `<patterns>`: one or more patterns joined by `,` with nothing in between. An empty pattern (for example from `a.b,` or `a.b,,c.d`) makes the list malformed. A pattern may appear more than once.
- `<response>`: either the word `timeout` (lowercase), or exactly three digits whose value is from `100` to `599` inclusive.
- `<timestamp>`: one or more digits `0` to `9`. Leading zeros are allowed (`007` is 7). No sign, no decimal point.

### Pattern matching

- The pattern `*` on its own matches **every** event type, whatever its number of segments.
- Any other pattern matches an event type if and only if they have the **same number of segments** and every pattern segment is either `*` or exactly equal to the event type segment at the same position. So inside a longer pattern, `*` stands for exactly one segment.

| Pattern | Matches | Does not match |
|---|---|---|
| `charge.*` | `charge.succeeded` | `charge`, `charge.dispute.created` |
| `*.created` | `customer.created` | `charge.dispute.created` |
| `customer.*.updated` | `customer.subscription.updated` | `customer.updated` |
| `*` | `charge`, `invoice.paid`, `a.b.c.d` | |

An endpoint matches an event if at least one of its patterns matches the event type. A matching endpoint gets exactly **one** delivery for that event, even if several of its patterns match.

### REGISTER

`REGISTER <endpoint_id> <patterns>` registers a new endpoint with the given patterns. Its configured response is `200`. The endpoint only receives events emitted after it was registered.

### SET_STATUS

`SET_STATUS <endpoint_id> <response>` changes the configured response of an existing endpoint. It applies to every attempt made from now on, including attempts of deliveries that were created before this command.

### EMIT

`EMIT <event_id> <event_type>` emits a new event. For every registered endpoint that matches the event type, one delivery is created, scheduled at the current clock value. It is valid for an event to match no endpoint (then no delivery is created). Event ids must be unique: an id that was used by an earlier **valid** `EMIT` cannot be used again.

### TICK

`TICK <timestamp>` sets the clock to `timestamp` and then attempts every delivery that is scheduled at or before `timestamp` and has not been attempted yet. (In this part, that is every delivery that has not been attempted yet.) The timestamp may be equal to the current clock.

Deliveries are attempted in this order:

1. by event, in the order the events were emitted (earliest first);
2. deliveries of the same event, by endpoint id in increasing lexicographic order, comparing the ids character by character by their ASCII codes. For example `we_1` < `we_10` < `we_9` < `we_a`.

Each attempt uses the endpoint's configured response **at the moment the `TICK` is processed** (not at the moment the event was emitted). Each attempt prints exactly one line:

```
<time> <event_id> <endpoint_id> <attempt> <response> <result>
```

- `<time>`: the time of the attempt, which is the delivery's **scheduled** time (the clock value when the event was emitted), printed as a decimal integer without leading zeros. It can be smaller than the `TICK` timestamp.
- `<attempt>`: the attempt number of this delivery. In this part it is always `1`.
- `<response>`: the configured response exactly as it was given in `SET_STATUS` (or `200` if it was never set).
- `<result>`: `OK` if the attempt is a success, `FAILED` otherwise.

A `TICK` with nothing to attempt prints nothing.

### Invalid commands

A command is invalid, prints the single line `INVALID` and changes nothing, if any of the following holds:

- a field is empty (leading space or two consecutive spaces);
- the command name is not exactly one of `REGISTER`, `SET_STATUS`, `EMIT`, `TICK`;
- the number of fields is wrong (`REGISTER`, `SET_STATUS` and `EMIT` have exactly 3 fields, `TICK` has exactly 2);
- `REGISTER`: the endpoint id is malformed or already registered, or the pattern list is malformed;
- `SET_STATUS`: no registered endpoint has this id (this includes malformed ids), or the response is malformed;
- `EMIT`: the event id is malformed or was used by an earlier valid `EMIT`, or the event type is malformed;
- `TICK`: the timestamp is malformed, or it is smaller than the current clock.

Valid `REGISTER`, `SET_STATUS` and `EMIT` commands print nothing.

## Function Description

Complete the function `deliverWebhooks` in the editor below.

`deliverWebhooks` has the following parameter:

- `string commands[n]`: the commands, in chronological order

Returns:

- `string[]`: all printed lines, in the order they are printed: `INVALID` for each invalid command, and the attempt lines of each `TICK`

## Constraints

- `1 ≤ n ≤ 10^4`
- Each command has between 1 and 100 characters, made of printable ASCII characters and spaces, with no trailing whitespace.
- Every timestamp made only of digits has a value of at most `10^9`.
- At most 300 endpoints are registered.

## Input Format For Custom Testing

The first line contains an integer, `n`, the number of commands.
Each of the next `n` lines contains a string, `commands[i]`.

## Sample Case 0

### Sample Input For Custom Testing

```
9
REGISTER we_a charge.*
REGISTER we_b *,invoice.paid
EMIT evt_1 charge.succeeded
EMIT evt_2 charge.dispute.created
SET_STATUS we_b 500
TICK 10
SET_STATUS we_b 204
EMIT evt_3 invoice.paid
TICK 10
```

### Sample Output

```
0 evt_1 we_a 1 200 OK
0 evt_1 we_b 1 500 FAILED
0 evt_2 we_b 1 500 FAILED
10 evt_3 we_b 1 204 OK
```

### Explanation

- `we_a` subscribes to `charge.*`. `we_b` subscribes to `*` and `invoice.paid`. Both answer `200`.
- `EMIT evt_1 charge.succeeded` at clock 0: `charge.*` matches (two segments each) and `*` matches, so two deliveries are scheduled at time 0.
- `EMIT evt_2 charge.dispute.created`: `charge.*` has two segments but the type has three, so `we_a` does not match. `we_b` matches through `*`. One delivery, scheduled at time 0.
- `SET_STATUS we_b 500`: from now on `we_b` answers `500`.
- `TICK 10`: the three deliveries are attempted in event order, then endpoint id order. The printed time is the scheduled time 0, not 10. `we_a` answers `200` (`OK`), `we_b` answers `500` twice (`FAILED`). Every delivery is now finished.
- `SET_STATUS we_b 204`, then `EMIT evt_3 invoice.paid` at clock 10. Both of `we_b`'s patterns match, but it gets only one delivery. `we_a` does not match.
- `TICK 10`: equal to the current clock, so it is valid. The delivery scheduled at 10 is attempted. `204` is between 200 and 299, so the result is `OK`.

## Sample Case 1

### Sample Input For Custom Testing

```
13
REGISTER we_9 *.created
REGISTER we_10 customer.*
REGISTER we_9 *
REGISTER we_c charge*
SET_STATUS we_10 timeout
SET_STATUS we_x 200
EMIT evt_1 customer.created
TICK 5
TICK 4
EMIT evt_1 invoice.created
SET_STATUS we_9 302
EMIT evt_2 invoice.created
TICK 5
```

### Sample Output

```
INVALID
INVALID
INVALID
0 evt_1 we_10 1 timeout FAILED
0 evt_1 we_9 1 200 OK
INVALID
INVALID
5 evt_2 we_9 1 302 FAILED
```

### Explanation

- `we_9` subscribes to `*.created` and `we_10` subscribes to `customer.*`.
- `REGISTER we_9 *` is `INVALID`: `we_9` is already registered.
- `REGISTER we_c charge*` is `INVALID`: a pattern segment must be exactly `*` or contain no `*` at all.
- `SET_STATUS we_10 timeout` is valid. `SET_STATUS we_x 200` is `INVALID` because `we_x` is not registered.
- `EMIT evt_1 customer.created` matches both endpoints.
- `TICK 5`: `we_10` comes before `we_9` because the ids are compared as strings (`1` < `9` at the fourth character). `we_10` times out (`FAILED`) and `we_9` answers `200` (`OK`).
- `TICK 4` is `INVALID`: the clock is already 5.
- `EMIT evt_1 invoice.created` is `INVALID`: `evt_1` was already emitted.
- `SET_STATUS we_9 302`, then `EMIT evt_2 invoice.created` at clock 5 matches only `we_9`.
- `TICK 5`: `302` is not between 200 and 299, so the attempt is `FAILED`.
