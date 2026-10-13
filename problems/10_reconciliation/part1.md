# Invoice Reconciliation: Part 1

You are building the matching engine behind a finance team's reconciliation tool. The engine reads one chronological stream of records. Some records are **invoices** that the company issued to its customers. Others are **bank lines**, the incoming credits from the company's bank statement feed. Each incoming bank line should be matched to the invoice that it pays. Lines that cannot be matched are kept in an unmatched queue for a human to review.

An **invoice** has an id, a customer name, an amount, an issue date, an applied amount (the money matched to it so far, which starts at `0.00`) and a status. In this part the status is `open` (nothing has been applied) or `paid`.

A **bank line** has a transaction id, a value date, an amount and a free-text memo written by the payer's bank. Every accepted bank line is either matched to exactly one invoice or unmatched.

Both kinds of record arrive as CSV text, and the feed is not always clean. Parsing the records exactly as specified below is a core part of the task.

## Commands

Each command is a single string that holds one CSV record. The first field is the record type. The record types are case sensitive.

### CSV format

A record is a sequence of fields separated by commas. The number of fields is the number of separating commas plus one, so `STATUS,` has two fields and the second one is empty. Each field is either unquoted or quoted:

- An **unquoted field** is zero or more characters, none of which is a comma or a double quote (`"`). Its value is exactly those characters. Spaces are kept and never trimmed.
- A **quoted field** starts with `"` as its very first character. Read the characters after the opening quote from left to right. Two consecutive quotes (`""`) stand for one literal `"` character. A single `"` that is not followed by another `"` is the closing quote. Every other character, commas included, stands for itself. The closing quote must be the last character of the command or be followed directly by a comma. The value is the text between the quotes, with each `""` replaced by `"`.

A record is **malformed** if any of these is true:

- an unquoted field contains a `"` character (for example `ab"c`, or ` "abc"` with a leading space, because that field does not start with a quote),
- a quoted field has no closing quote (for example `"abc` or `"a""b`),
- the closing quote of a quoted field is followed by anything other than a comma (for example `"abc"d` or `"abc" ,`).

All later rules are about field **values**. Quoting a field does not change its meaning, so `"STATUS","inv_0001"` is the same command as `STATUS,inv_0001`.

### Field formats

- `invoice_id`: `inv_` followed by exactly 4 digits, for example `inv_0012`.
- `txn_id`: `txn_` followed by 1 to 8 digits, for example `txn_9`. Ids are compared as exact strings, so `txn_7` and `txn_07` are different ids.
- `amount`: 1 to 9 digits, a `.`, then exactly 2 digits. The value must be greater than zero. Leading zeros are allowed and amounts are compared by numeric value, so `007.50` equals `7.50`. Signs, spaces, thousands separators and any other form are not allowed.
- `date`: `YYYY-MM-DD` with exactly 4, 2 and 2 digits. It must be a real Gregorian calendar date (leap years included) with a year from 2000 to 2099 inclusive.
- `customer`: any non-empty value.
- `memo`: any value, possibly empty.

| Command | Format | Output |
|---|---|---|
| Invoice | `INVOICE,<invoice_id>,<customer>,<amount>,<date>` | `OK` |
| Bank line | `BANK,<txn_id>,<date>,<amount>,<memo>` | `MATCHED <invoice_id>` or `UNMATCHED` |
| Status | `STATUS,<invoice_id>` | `<invoice_id> <status> <applied> <amount>` |
| Unmatched queue | `UNMATCHED` | the unmatched transaction ids, or `NONE` |

Every command produces exactly one output line.

### INVOICE

Creates an invoice with status `open` and applied amount `0.00`. Output `OK`.

### BANK

Records the bank line and immediately tries to match it.

1. Split the memo into **tokens**. A token is a maximal run of consecutive characters that are ASCII letters, digits or underscores. Every other character separates tokens. For example, the memo `Paid: inv_0012/inv_0013, thanks!` has the tokens `Paid`, `inv_0012`, `inv_0013` and `thanks`. The memo `INV-0013` has the tokens `INV` and `0013`.
2. Look at the tokens in memo order. The line matches the **first** token that satisfies all of the following:
   - the token is exactly equal (case sensitive) to the id of an existing invoice,
   - that invoice's status is `open`,
   - that invoice's amount equals the bank line amount.
   Tokens that fail any condition are skipped.
3. If a token matches, that invoice's applied amount becomes the bank amount and its status becomes `paid`. Output `MATCHED <invoice_id>`.
4. Otherwise the bank line is unmatched. Output `UNMATCHED`.

A bank line is matched only at the moment it is received. An invoice created later never causes an earlier bank line to be matched, and an unmatched line stays unmatched.

Records are not in date order. Dates may go backwards from one record to the next. Dates are stored, but they do not affect matching in this part.

### STATUS

Outputs `<invoice_id> <status> <applied> <amount>`, where both amounts are printed with exactly 2 decimal places, for example `inv_0012 paid 1250.00 1250.00` or `inv_0013 open 0.00 300.00`.

### UNMATCHED

Outputs the transaction ids of all bank lines that are currently unmatched, separated by single spaces. They are sorted by bank date ascending. Ties are broken by the order in which their `BANK` commands appeared in the input. If there are no unmatched lines, output `NONE`.

### Invalid commands

A command is invalid, outputs `ERROR` and has no effect if any of these is true:

- the record is malformed,
- the record type is not exactly one of `INVOICE`, `BANK`, `STATUS`, `UNMATCHED`,
- the number of fields is wrong (`INVOICE` has 5, `BANK` has 5, `STATUS` has 2, `UNMATCHED` has 1),
- any field value does not follow its format,
- an `INVOICE` uses an invoice id that already exists, or a `BANK` uses a transaction id that already exists,
- a `STATUS` names an invoice id that does not exist.

An invalid command does not reserve its ids. A later valid command may use them.

## Function Description

Complete the function `reconcileInvoices` in the editor below.

`reconcileInvoices` has the following parameter:

- `string commands[n]`: the commands, in chronological order

Returns:

- `string[]`: one output line per command, in command order

## Constraints

- `1 ≤ n ≤ 10^4`
- Each command has 1 to 200 characters. Every character is printable ASCII (codes 32 to 126). No command has trailing whitespace.

## Input Format For Custom Testing

The first line contains an integer, `n`, the number of commands.
Each of the next `n` lines contains a string, `commands[i]`.

## Sample Case 0

### Sample Input For Custom Testing

```
7
INVOICE,inv_0012,"ACME, Inc.",1250.00,2024-03-01
INVOICE,inv_0013,Globex,300.00,2024-03-02
BANK,txn_9,2024-03-04,1250.00,Payment ref: inv_0012 thanks
BANK,txn_10,2024-03-05,300.00,INV-0013
STATUS,inv_0012
STATUS,inv_0013
UNMATCHED
```

### Sample Output

```
OK
OK
MATCHED inv_0012
UNMATCHED
inv_0012 paid 1250.00 1250.00
inv_0013 open 0.00 300.00
txn_10
```

### Explanation

1. Invoice `inv_0012` is created for the customer `ACME, Inc.`. The name is quoted because it contains a comma. Output `OK`.
2. Invoice `inv_0013` is created for `Globex`. Output `OK`.
3. The memo has the tokens `Payment`, `ref`, `inv_0012` and `thanks`. `inv_0012` exists, is `open`, and its amount `1250.00` equals the bank amount. Output `MATCHED inv_0012`.
4. The memo `INV-0013` has the tokens `INV` and `0013`. Neither one is an invoice id, so the line is unmatched.
5. `inv_0012` has `1250.00` applied and is `paid`.
6. `inv_0013` has nothing applied and is `open`.
7. Only `txn_10` is unmatched.

## Sample Case 1

### Sample Input For Custom Testing

```
9
INVOICE,inv_0001,"Wayne ""WE"" Enterprises",99.50,2024-01-15
INVOICE,inv_0002,Initech,99.50,2024-01-20
BANK,txn_1,2024-01-21,99.50,"inv_0001,inv_0002"
BANK,txn_2,2024-01-22,99.50,"Re: "inv_0002"
BANK,txn_2,2024-01-22,99.50,Invoice inv_0001
BANK,txn_3,2024-01-20,99.50,"See ""inv_0002"""
BANK,txn_3,2024-01-25,10.00,retry
STATUS,inv_0003
UNMATCHED
```

### Sample Output

```
OK
OK
MATCHED inv_0001
ERROR
UNMATCHED
MATCHED inv_0002
ERROR
ERROR
txn_2
```

### Explanation

1. The customer value is `Wayne "WE" Enterprises`. Each `""` inside the quoted field is one literal quote. Output `OK`.
2. `inv_0002` is created. Output `OK`.
3. The memo value is `inv_0001,inv_0002`. The field is quoted, so the comma is part of the value. The first token `inv_0001` is open and its amount equals `99.50`, so the line matches it.
4. The quoted field `"Re: "` closes after `Re: `, and the closing quote is followed by `i` instead of a comma. The record is malformed: `ERROR`. Nothing is recorded, so `txn_2` is still free.
5. `txn_2` is accepted now. Its tokens are `Invoice` (not an invoice id) and `inv_0001`, which is already `paid`. Output `UNMATCHED`.
6. The memo value is `See "inv_0002"`. Its tokens are `See` and `inv_0002`, which is open with an equal amount. Output `MATCHED inv_0002`. Its date is earlier than the previous line's date, and that is allowed.
7. `txn_3` already exists: `ERROR`.
8. `inv_0003` does not exist: `ERROR`.
9. Only `txn_2` is unmatched.
