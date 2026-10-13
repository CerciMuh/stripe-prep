# Switchboard Config Store: Part 1

Switchboard is the internal configuration and feature-flag store used by backend services. Services write flags such as `checkout.v2:enabled` or `payouts.instant:limit`, read them on every request, and operators run quick queries to see which flags hold a given value. You are going to simulate Switchboard by processing a log of commands in order.

The store maps **keys** to **values**. A key either holds exactly one value or is absent. Values are arbitrary strings: they may contain spaces, quotes and backslashes, and they may be empty. Because of that, a value in a command can be written either as a plain word or as a double-quoted string with escapes, and parsing the command line correctly is a large part of the job.

The store starts empty. Every command produces exactly one output line.

## Commands

Each command is a single string of printable ASCII characters (codes 32 to 126). It is split into **tokens**, which are separated by one or more space characters. The first token is the timestamp, the second token is the command name, and the remaining tokens are the arguments.

**Tokenizing.** Read the command from left to right, skipping spaces between tokens.

- A token that does not start with `"` is a **bare token**: it runs until the next space or the end of the command. A bare token must not contain a `"` or a `\` character anywhere. If it does, the command is invalid.
- A token that starts with `"` is a **quoted token**. Its text is everything up to the next unescaped `"`, which closes the token. Inside a quoted token:
  - Spaces are ordinary characters and are kept exactly (including runs of several spaces).
  - `\"` stands for one `"` character and `\\` stands for one `\` character.
  - A `\` followed by any other character, or a `\` that is the last character of the command, makes the command invalid.
  - If the command ends before the closing `"`, the command is invalid.
  - The closing `"` must be followed by a space or by the end of the command. Anything else (for example `"a"b` or `"a""b"`) makes the command invalid.
  - The text of `""` is the empty string.

A lexical error anywhere in the command (even in a position whose value would not matter) makes the whole command invalid.

**Keys.** A key is a bare token of 1 to 64 characters, where every character is a lowercase letter `a`-`z`, a digit `0`-`9`, or one of `_` `.` `:` `-`. Keys are case sensitive.

**Values.** A value argument may be a bare token or a quoted token. The value is the token's text, so `on` and `"on"` are the same value. Values are compared exactly, character by character (case sensitive, spaces significant).

**Where quoting is allowed.** Only value arguments may be quoted. Any other token given as a quoted token (the command name, a key, a prefix) makes the command invalid, even if its text would otherwise be valid.

**Printing a value.** Whenever a value is printed, it is printed in quoted form: a `"`, then the value with every `\` replaced by `\\` and every `"` replaced by `\"`, then a closing `"`. For example the value `say "hi"` is printed as `"say \"hi\""`, and the empty value is printed as `""`.

| Command | Format | Output |
|---|---|---|
| SET | `<timestamp> SET <key> <value>` | `OK` |
| GET | `<timestamp> GET <key>` | the printed value, or `NOT_FOUND` |
| DELETE | `<timestamp> DELETE <key>` | `DELETED` or `NOT_FOUND` |
| COUNT | `<timestamp> COUNT <value>` | a non-negative integer |
| SCAN | `<timestamp> SCAN` or `<timestamp> SCAN <prefix>` | a listing, or `(empty)` |

**SET** stores the value under the key, replacing any previous value. Output `OK`.

**GET** outputs the key's value in printed form, or `NOT_FOUND` if the key is absent.

**DELETE** removes the key and outputs `DELETED`. If the key is absent, nothing changes and the output is `NOT_FOUND`.

**COUNT** outputs the number of keys that currently hold exactly the given value, as a decimal integer (`0` if none).

**SCAN** lists the keys that start with the prefix, together with their values. The prefix must satisfy the same rules as a key (bare, 1 to 64 allowed characters). A key equal to the prefix matches. `SCAN` with no argument lists every key. Each entry is written as `<key>=<printed value>`. Entries are sorted in ascending order of key, comparing characters by their ASCII codes (so `-` < `.` < digits < `:` < `_` < lowercase letters, and a key that is a prefix of another key comes first). Entries are joined by a single space. If no key matches, the output is `(empty)`.

Command names are case sensitive: `get` or `Get` is not a command.

### Invalid commands

A command is invalid if any of the following holds:

- It has a lexical error (see Tokenizing).
- The command name is not exactly one of `SET`, `GET`, `DELETE`, `COUNT`, `SCAN`, or it is a quoted token.
- It has the wrong number of arguments: `SET` takes exactly 2, `GET`, `DELETE` and `COUNT` take exactly 1, `SCAN` takes 0 or 1.
- A key or prefix argument is not a valid key (wrong characters, wrong length, or quoted).

An invalid command outputs `ERROR` and has no effect on the store.

## Function Description

Complete the function `runConfigStore` in the editor below.

`runConfigStore` has the following parameter:

- `string commands[n]`: the commands, in chronological order

Returns:

- `string[]`: exactly `n` lines, where line `i` is the output of `commands[i]`

## Constraints

- `1 ≤ n ≤ 10^4`
- Each command has at most 300 characters, all printable ASCII (codes 32 to 126), with no leading or trailing spaces.
- Every command starts with a well-formed timestamp: an integer from `0` to `10^9` with no leading zeros, followed by one or more spaces and at least one more character. Timestamps are non-decreasing. In this part they do not affect the result.
- Everything after the timestamp may be malformed and must be validated as described above.

## Input Format For Custom Testing

The first line contains an integer, `n`, the number of commands.
Each of the next `n` lines contains a string, `commands[i]`.

## Sample Case 0

### Sample Input For Custom Testing

```
10
1 SET checkout.v2:enabled on
2 SET checkout.banner "Holiday sale, 20% off"
3 GET checkout.banner
4 SET radar.mode on
5 COUNT on
6 SCAN checkout.
7 DELETE checkout.v2:enabled
8 GET checkout.v2:enabled
9 DELETE checkout.v2:enabled
10 SCAN payouts
```

### Sample Output

```
OK
OK
"Holiday sale, 20% off"
OK
2
checkout.banner="Holiday sale, 20% off" checkout.v2:enabled="on"
DELETED
NOT_FOUND
NOT_FOUND
(empty)
```

### Explanation

- `SET checkout.v2:enabled on` stores the bare value `on`. Output `OK`.
- `SET checkout.banner "Holiday sale, 20% off"` stores a value containing spaces, given as a quoted token. Output `OK`.
- `GET checkout.banner` prints the value in quoted form: `"Holiday sale, 20% off"`.
- `SET radar.mode on` stores `on`. Output `OK`.
- `COUNT on`: `checkout.v2:enabled` and `radar.mode` both hold `on`, so the output is `2`.
- `SCAN checkout.` matches `checkout.banner` and `checkout.v2:enabled`. `b` comes before `v`, so `checkout.banner` is listed first.
- `DELETE checkout.v2:enabled` removes the key. Output `DELETED`.
- `GET checkout.v2:enabled`: the key is absent. Output `NOT_FOUND`.
- `DELETE checkout.v2:enabled`: the key is already absent. Output `NOT_FOUND`.
- `SCAN payouts`: no key starts with `payouts`. Output `(empty)`.

## Sample Case 1

### Sample Input For Custom Testing

```
12
1 SET greeting "say \"hi\""
2 GET greeting
3 SET path "C:\\tmp"
4 GET path
5 SET empty ""
6 COUNT ""
7 SET bad "unterminated
8 SET bad "a\nb"
9 SET bad "a"b
10 get greeting
11 SET Bad x
12 SCAN
```

### Sample Output

```
OK
"say \"hi\""
OK
"C:\\tmp"
OK
1
ERROR
ERROR
ERROR
ERROR
ERROR
empty="" greeting="say \"hi\"" path="C:\\tmp"
```

### Explanation

- `SET greeting "say \"hi\""`: each `\"` stands for a `"`, so the stored value is `say "hi"`. Output `OK`.
- `GET greeting` prints the value with its quotes escaped again: `"say \"hi\""`.
- `SET path "C:\\tmp"`: `\\` stands for one backslash, so the value is `C:\tmp`. Output `OK`.
- `GET path` prints `"C:\\tmp"`.
- `SET empty ""` stores the empty string. Output `OK`.
- `COUNT ""`: only `empty` holds the empty string. Output `1`.
- `SET bad "unterminated`: the quoted token never closes. Output `ERROR`.
- `SET bad "a\nb"`: `\n` is not an allowed escape. Output `ERROR`.
- `SET bad "a"b`: the closing quote is followed by `b` instead of a space or the end. Output `ERROR`.
- `get greeting`: command names are case sensitive. Output `ERROR`.
- `SET Bad x`: keys may not contain uppercase letters. Output `ERROR`.
- `SCAN` with no prefix lists all three keys in ASCII order: `empty`, `greeting`, `path`. None of the invalid commands changed the store.
