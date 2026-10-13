# stripe-prep

Local drills for the Stripe New Grad SWE OA (HackerRank, 60 min, one problem in 4 stacked parts).
Every problem simulates a system: you process a chronological list of string commands, track
state, reject invalid operations and parse heavily. It is not LeetCode.

No solutions or hints live in this repo.

## Requirements

Python 3.10+. Stdlib only. No install step.

## Drill loop

```bash
./drill list                         # 10 problems + your best times
./drill start 03                     # OA mode, 60 min
./drill start 03 --mode screen       # team screen mode, 45 min
```

`start` copies a HackerRank-style stub to `attempts/<problem>/<timestamp>/solution.py` and prints
Part 1. The statement is also saved next to your solution. Edit only the function body.

```bash
./drill run                          # "Run Code": sample cases of the current part, with diffs
./drill run --custom my_input.txt    # "Run Code" with custom input
./drill submit                       # "Submit": hidden cases, parts 1..current, counts only
./drill next                         # unlock the next part (current part must be 100%)
./drill next --force                 # move on anyway (like the real OA when you are out of time)
./drill status                       # time left, time spent per part
./drill clock                        # live countdown, run it in a second terminal
./drill show                         # reprint unlocked statements
./drill end                          # stop the clock, log per-part times
./drill history                      # past drills
```

## Rules of the drill

- **One growing solution.** Each part extends the previous one. `submit` re-runs every earlier
  part's hidden tests, so a later part that breaks earlier behaviour costs you points, as in the real OA.
- **Parts unlock one at a time.** Later statements and every test live in `problems/*/.vault`.
  That file is compressed and encoded. It is not secret, so do not decode it.
- **HackerRank harness.** Your file runs as `python3 solution.py`, with input on stdin and output
  written to `$OUTPUT_PATH`. The time limit is 10s per test case. Output is compared line by line
  after trailing whitespace is stripped.
- **No AI autocomplete** in your editor while drilling. The real OA has none.
- **Treat the timer as real.** When time is up, `submit` still works but reports the overrun.

## Problems

| ID | Problem | Parsing flavour |
|---|---|---|
| 01 | Merchant Ledger | space separated, decimal money |
| 02 | API Gateway Rate Limiter | `key=value` config, path normalization |
| 03 | Switchboard Config Store | quoted strings with escapes |
| 04 | Subscription Billing | CSV-ish, calendar dates |
| 05 | Payment Intents | pipe delimited, `k=v;k=v` params |
| 06 | FX Conversion Service | decimals, rounding, currency codes |
| 07 | Fraud Rules Engine | rule expression grammar |
| 08 | Webhook Delivery | wildcard patterns, time simulation |
| 09 | Merchant Payouts | fees, schedules, decimal money |
| 10 | Invoice Reconciliation | strict CSV with quoting |

## Layout

```
drill                     CLI (single file)
problems/NN_slug/
  meta.json               title, parts, function name
  part1.md                Part 1 statement (later parts are in .vault)
  solution.py             empty HackerRank stub, copied on start
  .vault                  locked statements + test cases
attempts/                 your code (gitignored)
logs/history.jsonl        per-part timings (gitignored)
```

## Coming later

- Bug Squash: a realistic multi-module library with failing tests and planted bugs.
- Integration: a local mock API (errors, timeouts, malformed JSON, pagination, rate limits) plus docs.
