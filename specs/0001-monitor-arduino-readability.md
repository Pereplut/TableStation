---
title: Readability refactor of MonitorArduino.py and its monitor.py call path
status: draft
packages: [MonitorArduino.py, monitor.py]
---

## Problem & why

`MonitorArduino.py` is the entry point that polls the Arduino over serial and stores DHT11 readings.
It is 28 lines, but it and the `monitor.py` code it drives are hard to read and easy to misread.
Observed in the current tree (commit `4152a8f`):

| # | Issue | Evidence |
|---|---|---|
| R1 | All work runs at module top level with no `main()` and no `if __name__ == "__main__":` guard; importing the file opens the serial port and enters an infinite loop. | `MonitorArduino.py:5-28` |
| R2 | Misleading comment copied from the Python logging cookbook ("spam_application"), plus comments that restate the next line. | `MonitorArduino.py:4`, `:7`, `:10`, `:13`, `:17` |
| R3 | Commented-out code left in place. | `MonitorArduino.py:23`, `:26`; `monitor.py:45`, `:49`, `:54`, `:67`, `:70`, `:75` |
| R4 | Magic values inline: port, baud rate, read timeout, poll command, poll interval, log file name. | `MonitorArduino.py:8`, `:22`; `monitor.py:16-17`, `:50`, `:64`, `:71`, `:83` |
| R5 | Misspelled identifiers: `recive`, `responce`; mixed naming styles (`readFrom_Serial`, `messageThis`, `Temperature`, `Light` as local variable names). | `monitor.py:40`, `:51`, `:72`, `:47`, `:36`, `:58`, `:60` |
| R6 | Duplicated poll loop: `readFrom_Serial` and `read_dht11_serial` are the same loop with a different parse and different rows; only the second is called. | `monitor.py:47-65` vs `:68-84`; caller `MonitorArduino.py:27` |
| R7 | One function mixes four responsibilities: serial I/O, parsing, persistence and pacing. | `monitor.py:68-84` |
| R8 | Statement with no effect: the result of `str.strip` is discarded, so the line reads as if whitespace were removed when it is not. | `monitor.py:53`, `:74` |
| R9 | Log call with an unfilled `%s` placeholder: the message logged literally contains `%s`. | `monitor.py:52`, `:73` |
| R10 | Unreachable code after `while True:`. | `monitor.py:65`, `:84` |
| R11 | Logger names do not match the entry point's logger: handlers are attached to `Arduino_app`, while `monitor.py` logs to `app.mon_While` / `app.mon_While.ArduinoSerial`, which are not its children, so none of `monitor.py`'s INFO messages reach `serial_monitor.log` or the console. A reader assumes they do. | `MonitorArduino.py:5`, `:18-19`; `monitor.py:9`, `:20` |
| R12 | Inconsistent error handling: `ArduinoSerial.open` prints and calls `exit()` on `SerialException` but is never called (the constructor already opens the port and raises unhandled); every other failure propagates. | `monitor.py:24-29`, `:18` |
| R13 | Import-time side effects in `monitor.py`: DB engine and a global session are created on import. | `monitor.py:10-13` |
| R14 | Unused parsed field `status` and no docstrings anywhere. | `monitor.py:77`; both files |

Why: the next change to this loop (new sensor, error handling, port configuration) will be made by
someone reading this code; today the code says things it does not do (R8, R9, R11, R12).

## Goals / Non-goals

**Goals**
- Make `MonitorArduino.py` and the `monitor.py` call path it uses read accurately: names, structure,
  constants, comments and docstrings that match what the code does.
- Keep every observable behaviour identical, proven by characterization tests written against the
  pre-refactor code and run unchanged against the refactored code.

**Non-goals**
- No change to the serial protocol (port settings, the `"1"` poll command, line format).
- No change to sensor reading, parsing results, or the values written to the database.
- No change to which tables are written, the database URL `sqlite:///tableStation.db`, or schema
  (`app/models.py` is out of scope, including its `timeStamp` default at `app/models.py:15`).
- No change to logging output: logger names, messages, levels, format, destinations.
- No change to timing: one poll per iteration, 60 s sleep, 5 s read timeout.
- No change to failure behaviour (which errors crash the process) — see `## [NEEDS CLARIFICATION]`.
- No change to `Receiver_API.py`, `app/`, `run.py`, `config.py`.

## User stories

- As the maintainer, I open `MonitorArduino.py` and can tell from names, constants and docstrings
  what port it opens, how often it polls and where readings go, without reading `monitor.py`.
- As the maintainer, I can change the poll interval or port in one named place.
- As the maintainer, after the refactor the station records exactly what it recorded before.

## Acceptance criteria (EARS)

### Behaviour preservation

- **AC-1** WHEN `MonitorArduino.py` is run as a script, the monitor shall open the serial port with
  `port='/dev/ttyACM0'`, `baudrate=115200`, `bytesize=EIGHTBITS`, `parity=PARITY_NONE`,
  `stopbits=STOPBITS_ONE`, `timeout=5`.
- **AC-2** WHILE the poll loop runs, the monitor shall write exactly the bytes `b"1"` to the serial
  port once per iteration, before reading a line.
- **AC-3** WHEN a non-empty line is read whose UTF-8 decoding splits on `,` into exactly three
  fields, the monitor shall add and commit exactly one `dht11` row whose `humidity` and
  `temperature` are byte-identical to the values the pre-refactor code stores for the same line
  (second and third field as stored today; see Q2).
- **AC-4** WHEN a reading is persisted, the monitor shall write no row to the `thermometer` or
  `photosell` tables.
- **AC-5** IF `readline` returns no data (read timeout), THEN the monitor shall add no row and
  perform no commit for that iteration.
- **AC-6** WHILE the poll loop runs, the monitor shall call `time.sleep(60)` exactly once per
  iteration, after the read, whether or not a row was written.
- **AC-7** IF a non-empty line does not split into exactly three comma-separated fields, THEN the
  monitor shall raise `ValueError` out of the loop with no row written for that line (current
  behaviour; see Q4).
- **AC-8** IF the bytes read are not valid UTF-8, THEN the monitor shall raise `UnicodeDecodeError`
  out of the loop with no row written for that line (current behaviour; see Q4).
- **AC-9** IF the serial port cannot be opened, THEN the monitor shall let `serial.SerialException`
  propagate and exit non-zero, after having logged `launching serial Monitoring` (current
  behaviour; see Q4).
- **AC-10** WHEN `MonitorArduino.py` is run as a script, the entry point shall emit, on logger
  `Arduino_app` at INFO, the messages `launching serial Monitoring`, `launched an instance of serial
  Monitoring`, `starting monitoring loop` in that order, to both `serial_monitor.log` and the
  console, with format `%(asctime)s - %(name)s - %(levelname)s - %(message)s`.
- **AC-11** The `monitor.py` code shall log under the logger names `app.mon_While` and
  `app.mon_While.ArduinoSerial`, with the same messages at the same levels and in the same order per
  iteration as before the refactor, except that the literal `%s` of R9 is the only text that may
  change (see Q3).
- **AC-12** The monitor shall persist through the database URL `sqlite:///tableStation.db`,
  resolved relative to the process working directory as today.
- **AC-13** WHEN a three-field line is persisted, the monitor shall not store or validate the first
  field (`status`), as today.

### Readability

- **AC-14** `MonitorArduino.py` shall contain at module level only imports, constants, function or
  class definitions, a module docstring, and a single `if __name__ == "__main__":` block; importing
  it shall open no serial port and add no log handler.
- **AC-15** The serial port path, baud rate, read timeout, poll command, poll interval in seconds and
  log file name shall each be a named UPPER_CASE module-level constant, and the literals
  `'/dev/ttyACM0'`, `115200`, `60`, `"1"` and `'serial_monitor.log'` shall not appear inside any
  function body in `MonitorArduino.py` or `monitor.py`.
- **AC-16** `MonitorArduino.py` and `monitor.py` shall contain no comment line that parses as a
  Python statement or expression (commented-out code).
- **AC-17** `MonitorArduino.py` and `monitor.py` shall contain no identifier containing `recive`,
  `responce` or `messageThis`, and every function and local variable name shall be `snake_case`.
- **AC-18** Parsing a serial line into the stored values shall be a function that takes a `str` and
  returns the values, performs no I/O, and is called from the poll loop.
- **AC-19** No function in `MonitorArduino.py` or `monitor.py` shall exceed 25 lines from its `def`
  line to its last line, docstring included.
- **AC-20** Each module, class and public function in `MonitorArduino.py` and `monitor.py` shall have
  a docstring.
- **AC-21** `MonitorArduino.py` and `monitor.py` shall contain no expression statement whose value is
  discarded and that has no side effect (the R8 `strip` call), and no statement after a
  `while True:` loop that has no `break`.
- **AC-22** No logging call in `MonitorArduino.py` or `monitor.py` shall pass a message containing a
  `%` placeholder without a matching argument.
- **AC-23** `MonitorArduino.py` and `monitor.py` shall contain no comment mentioning `spam`.
- **AC-24** The poll loop body shall exist once: `MonitorArduino.py` and `monitor.py` shall not
  contain two functions that each send the poll command and read a line (R6; how is Q1).

## Edge cases

Behaviour each one has today, which the refactor must keep (criterion in brackets):

- Read timeout, Arduino silent or unplugged after start: `readline` returns `b''`, nothing stored,
  sleep 60 s, poll again (AC-5, AC-6).
- Arduino unplugged at start / wrong port: `SerialException` from `serial.Serial(...)`, traceback,
  non-zero exit; `ArduinoSerial.open` is not involved (AC-9).
- Malformed line, wrong field count (e.g. a partial line after the 5 s timeout, or a boot banner):
  `ValueError` from tuple unpacking, process exits, `ending monitoring loop` never logged (AC-7).
- Non-UTF-8 bytes (line noise, baud mismatch): `UnicodeDecodeError`, process exits (AC-8).
- Line with three fields but non-numeric values, e.g. `nan`: stored as-is into String columns (AC-3).
- Line terminated by `\r\n`: the terminator is not stripped today (R8), so it stays in the third
  field as stored (AC-3; Q2).
- Whitespace-only line, e.g. `\r\n`: non-empty, one field, `ValueError` (AC-7).
- DB locked or unwritable: `commit` raises, process exits; unchanged, no criterion beyond AC-3.
- Line longer than any buffer: `readline()` has no size limit and returns at newline or timeout;
  unchanged.

## Non-functional

- Runtime: Python 3 as invoked today (shebang `#!/usr/bin/python3.4`); the refactor shall not
  require a newer interpreter than the one the station runs (version not confirmed; see Not
  specified in the report).
- No new runtime dependencies.
- What this spec cannot guarantee: AC-1 to AC-13 are only as strong as the characterization tests;
  a behaviour no test pins (for example exact log timing) is not protected. AC-14 to AC-24 are
  static properties of the two files and can be checked by a script; AC-1 to AC-13 need tests with a
  fake serial port and a temporary SQLite database.

## Inputs (provenance)

| Input | Source | Provenance | Notes |
|---|---|---|---|
| Serial line from Arduino | `serial.Serial.readline()` on `/dev/ttyACM0` | [reused: `monitor.py` `ArduinoSerial`] | Format `status,humidity,temperature` plus line terminator, set by Arduino firmware not in this repo |
| Serial port settings | literals in `MonitorArduino.py:22`, `monitor.py:16-17` | [deterministic: constants] | Become named constants (AC-15) |
| DB session | `monitor.py:10-13` | [reused: `app/models.py` `DHT11Table`, `Base`] | URL unchanged (AC-12) |
| Log configuration | `MonitorArduino.py:5-19` | [deterministic: constants] | Output unchanged (AC-10, AC-11) |

## Untrusted inputs

- **Serial line from the Arduino.** Written by device firmware outside this repository; any USB
  device enumerating as `/dev/ttyACM0` could send it. It is data, never instruction: the refactor
  shall not evaluate, format-string or shell out with it. Today it reaches the database only as bound
  ORM parameters (`DHT11Table(temperature=..., humidity=...)`), which the refactor keeps; it must
  not be interpolated into SQL or into a log format string (it may only be a logging argument).
  No length or content validation exists today and none is added (behaviour preservation); values
  are later rendered by the Flask app, whose templates are out of scope.

## [NEEDS CLARIFICATION]

1. **Q1 Scope and the legacy loop.** Does the refactor cover `monitor.py` (`ArduinoSerial`,
   `read_dht11_serial`, `readFrom_Serial`) or only `MonitorArduino.py`? And is `readFrom_Serial`
   (temperature/light, `monitor.py:47-65`, not called anywhere) deleted or kept behind a shared loop?
   Proposed default: both files in scope; `readFrom_Serial` deleted. Narrow scope drops AC-11,
   AC-13, AC-17 to AC-24 for `monitor.py`, leaving most issues (R5-R13) in place. Keeping
   `readFrom_Serial` means a shared loop with a pluggable parse/persist step, which is more code to
   read than the one path in use.
2. **Q2 Line terminator in stored values.** Today `strip` is a no-op (R8), so the stored
   `temperature` keeps the line terminator. Preserve (remove the no-op, values unchanged) or fix
   (apply the strip, stored values change)? Proposed default: preserve; fix in a separate spec.
   Fixing changes DB contents and whatever the web view shows, which breaks this spec's non-goal.
3. **Q3 Logger wiring.** `monitor.py` INFO messages never reach the log file or console (R11).
   Preserve (keep names; document it in a comment) or fix (make `monitor.py` loggers children of the
   configured logger, or configure the root logger), which adds lines to `serial_monitor.log`?
   Proposed default: preserve. Also: may the literal `%s` in the message (R9) be dropped, or filled
   with the received line? Proposed default: drop it; filling it would expose serial data in logs
   only if Q3 is "fix".
4. **Q4 Error handling.** Malformed lines, bad UTF-8 and a missing port all crash the process today
   (AC-7, AC-8, AC-9), and the dead `ArduinoSerial.open` suggests print-and-exit was once intended.
   Preserve crashes and delete or keep `open()`? Or change to log-and-skip for bad lines? Proposed
   default: preserve crashes, keep `open()`/`close()` untouched as public methods. Log-and-skip is a
   behaviour change (the station keeps running through noise) and belongs in its own spec.

## Test plan

Characterization tests are written first, run green against the pre-refactor code, and run unchanged
after. They use a fake serial object, a temporary SQLite session patched over `monitor.session`, and
a patched `time.sleep` that stops the loop after N iterations.

| Criteria | Test | Kind |
|---|---|---|
| AC-1 | Patch `serial.Serial`, run the entry point, assert constructor kwargs | characterization |
| AC-2 | Fake serial records writes; two iterations give `[b"1", b"1"]`, each before a `readline` | characterization |
| AC-3 | Feed `b"0,45.00,23.00\r\n"`; assert one `dht11` row equal to the pre-refactor fixture; negative: feed `b""`, assert zero rows | characterization |
| AC-4 | After AC-3 run, `thermometer` and `photosell` row counts are 0 | characterization |
| AC-5 | Feed `b""`; assert no row and commit not called; negative: valid line, commit called once | characterization |
| AC-6 | Patched `sleep` records `[60]` per iteration for both a valid and an empty read | characterization |
| AC-7 | Feed `b"45.00,23.00\r\n"` and `b"\r\n"`; assert `ValueError`, zero rows; negative: three-field line accepted | characterization |
| AC-8 | Feed `b"\xff\xfe\r\n"`; assert `UnicodeDecodeError`, zero rows | characterization |
| AC-9 | Patch `serial.Serial` to raise `SerialException`; run script in subprocess, assert non-zero exit and `launching serial Monitoring` in output | characterization |
| AC-10 | Run entry point with patched serial in a temp cwd; compare `serial_monitor.log` lines (timestamps masked) to pre-refactor capture | characterization |
| AC-11 | Capture records with a handler on `app.mon_While`; compare names, levels and messages to pre-refactor capture | characterization |
| AC-12 | Assert `monitor.engine.url` renders `sqlite:///tableStation.db` | unit |
| AC-13 | Feed `b"BAD,45.00,23.00\r\n"`; row is written, no column holds `BAD` | characterization |
| AC-14 | Import `MonitorArduino` with `serial.Serial` patched to fail the test if called; assert no handler added to `Arduino_app` | unit |
| AC-15 | AST script: constant names exist at module level; listed literals absent from function bodies | static script |
| AC-16 | Script: every `#` comment line, stripped of `#`, fails `ast.parse`; negative: a prose comment passes | static script |
| AC-17 | AST script: identifier blacklist and `snake_case` regex over function and local names | static script |
| AC-18 | Unit test calls the parse function with `"0,45.00,23.00\r\n"` with serial and DB unpatched-but-unavailable; asserts returned values equal the AC-3 fixture | unit |
| AC-19 | AST script: `end_lineno - lineno + 1 <= 25` for every function | static script |
| AC-20 | AST script: `ast.get_docstring` non-empty for module, classes, public functions | static script |
| AC-21 | AST script: no `Expr` node whose value is a call to `str.strip`/attribute with discarded result; no statement after `while True` without `break` | static script |
| AC-22 | AST script: logging calls whose message contains `%s`/`%d` have at least as many extra args | static script |
| AC-23 | Grep `-i spam` in both files returns nothing | static script |
| AC-24 | AST script: count functions that both call the send method with the poll command and call the receive method; expect at most 1 | static script |

AC-14 to AC-24 (11 of 24) are artifact properties a script can enforce; AC-1 to AC-13 depend on the
characterization tests being written before the refactor.

## Phases

| Phase | Date | Note |
|---|---|---|
| Initiation | | |
| Planning | | |
| Implementation | | |
| Validation | | |
| Completion | | |
