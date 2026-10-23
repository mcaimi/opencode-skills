# Frida CLI Reference

This reference covers the Frida tool family used for dynamic/runtime binary
analysis: the `frida` CLI/REPL, `frida-ps`, `frida-trace`, `frida-discover`,
`frida-kill`, and `gum-graft`. It assumes you've already read the
[Dynamic Analysis Consent Gate](../SKILL.md#dynamic-analysis-consent-gate) and
[Destructive/Impactful Dynamic Operations Gate](../SKILL.md#destructiveimpactful-dynamic-operations-gate)
in `SKILL.md` — this file is "how to invoke the tools," not "when you're
allowed to." For writing the JavaScript payloads these tools load, see
[FRIDA_JS_API_REFERENCE.md](FRIDA_JS_API_REFERENCE.md). For static analysis,
see [RAFIND2_REFERENCE.md](RAFIND2_REFERENCE.md).

## When to reach for dynamic vs. static analysis

Static analysis (`rafind2`/`r2`/`rabin2`) answers "what's in this file."
Dynamic analysis (Frida) answers "what does this program actually do when it
runs" — which API calls it makes, what inputs reach a given function, how
control flow branches at runtime, and what's in memory at a given moment.
Reach for Frida when:

- Static strings/signatures don't explain *how* a feature is implemented.
- The binary is packed, obfuscated, or otherwise resists static analysis.
- You need argument/return values for a specific function call, not just its
  presence in the import table.
- You need to observe behavior that only manifests at runtime (decrypted
  config, generated keys, network addresses resolved dynamically).

Dynamic analysis never replaces static analysis — correlate runtime addresses
back to static offsets/symbols via `r2`/`rabin2` whenever possible.

## Frida's Modes of Operation

| Mode | Description | When it applies |
|---|---|---|
| **Injected** | Frida injects its agent into a running or newly spawned process via ptrace/task-port APIs. | Default mode for local processes you can spawn or attach to; requires no changes to the target binary. |
| **Embedded (Preloaded)** | The Frida agent is loaded into the process at startup via a preload mechanism (e.g. `LD_PRELOAD`/`DYLD_INSERT_LIBRARIES`). | Useful when Injected mode is blocked but you control process startup (e.g. your own launcher script). |
| **Preloaded (frida-gadget as a shared library)** | `frida-gadget` is linked or loaded as a shared library inside the target, listening for a Frida client to connect. | Mobile apps, hardened binaries, or any target you can rebuild/repackage to include the gadget. |
| **Gadget (standalone config)** | `frida-gadget` runs with a `config.json` controlling autostart behavior (run an embedded script immediately, or wait for a connection). | When Injected mode is unavailable (SIP/hardened runtime/codesigning on macOS, locked-down Linux) and you can place the gadget library next to the target. |

For this phase (local Linux/macOS processes), start with **Injected mode**
(plain `frida`/`frida-trace`/`frida-discover` with `-f`/`-p`/`-n`) and fall
back to **Gadget** only when Injected mode is confirmed blocked by a platform
caveat (see `SKILL.md` Prerequisites).

## `frida` — CLI and REPL

```bash
# Spawn a new process (paused at entry) and load a script
frida -f /path/to/binary -l script.js

# Spawn and let it resume immediately
frida -f /path/to/binary -l script.js --no-pause

# Attach to a running process by PID
frida -p 1234 -l script.js

# Attach to a running process by name
frida -n "TargetApp" -l script.js

# Open a REPL against a spawned/attached target without a script
frida -f /path/to/binary
```

Inside the REPL, you have the same JavaScript API available (`Interceptor`,
`Memory`, `Process`, `Module`, `Stalker`) for ad hoc exploration before
committing to a script. `%resume` resumes a paused spawn from the REPL.

USB/remote device flags (`-U`, `-D <id>`, `-R`) exist but are **out of scope**
for this phase — this skill only targets local processes.

## `frida-ps` — Process Inspector

```bash
# List running processes (local)
frida-ps

# Include process names matching a filter (shell-side, not a frida-ps flag)
frida-ps | grep -i target
```

Use this to resolve a process name to a PID before `-p` attach, and to
confirm a target exists before using `frida-kill` or any destructive
operation. USB/remote flags (`-U`/`-D`) are out of scope here too.

## `frida-trace` — Dynamic Function Call Tracer

```bash
# Trace a specific exported function by name, attaching to a running process
frida-trace -i "open" -p 1234

# Trace a function when spawning a binary fresh
frida-trace -i "connect" -f /path/to/binary

# Trace by module + function (reduces false positives when the name is common)
frida-trace -i "libc.so!open" -p 1234

# Exclude noisy functions from a broad include pattern
frida-trace -i "*alloc*" -x "*free*" -p 1234

# Trace Objective-C methods (macOS) or Java methods (not applicable here —
# local native process scope), using -m for method patterns
frida-trace -m "-[NSString *]" -p 1234
```

Key flags: `-i <pattern>` include, `-I <module>` restrict to a module,
`-x <pattern>` exclude, `-X <module>` exclude a module, `-m <pattern>` for
Objective-C methods, `-j '<module>!<offset>'` to trace a raw address. Running
`frida-trace` generates a `__handlers__/` directory with one auto-generated
JS handler file per matched function — edit these in place to log
arguments/return values beyond the default, then re-run `frida-trace` to pick
up the edits (it's a stateful, editable scaffold, not a one-shot command).

## `frida-discover` — Finding Trace Candidates

```bash
# Enumerate a running process's internal (non-exported) functions as
# candidates for tracing
frida-discover -p 1234
```

`frida-discover` instruments the target to record which internal functions
get called during normal operation, then reports them as addresses/offsets
you can feed into `frida-trace -j` or a custom `Interceptor.attach` by
address. This is the bridge between "I don't know what to trace yet" and
`frida-trace`'s pattern-based tracing, which needs a name or address to start
from.

## `frida-kill` — Terminate a Process

```bash
frida-kill 1234
frida-kill "TargetApp"
```

Covered by the
[Destructive/Impactful Dynamic Operations Gate](../SKILL.md#destructiveimpactful-dynamic-operations-gate)
in `SKILL.md` — explicit request only, confirm the target against `frida-ps`
first.

## `gum-graft` — Binary Patching at the Gum Level

`gum-graft` is an example/utility tool built from the `frida-gum` source tree
(Meson+Ninja) — it is **not** installed by `uv tool install frida-tools`.
Before using it:

1. Confirm it's built and on `PATH` (`which gum-graft`). If not, point the
   user to https://github.com/frida/frida-gum and stop — this skill does not
   build it for them.
2. Treat it the same as `rafind2 -R`: explicit request only, work against a
   disposable copy of the target where possible.

Typical usage grafts a code stub/hook directly into a binary at the Gum ABI
level, lower-level than a JS `Interceptor.attach` — useful when you need the
hook to persist without a live Frida session, or when injecting into a
context a JS agent can't reach. Consult `gum-graft --help` for the exact
invocation your build provides, since it's example tooling rather than a
stable, versioned CLI.

## Stalker — Orientation

Stalker is Frida's code-tracing engine: it can follow a thread instruction by
instruction or basic-block by basic-block, re-emitting (and optionally
transforming) the code as it executes, which is what makes code-flow
reconstruction and full execution tracing possible without static
disassembly alone. At the CLI level there's no standalone `frida-stalker`
tool — Stalker is driven entirely from a JS agent via `Stalker.follow()`. See
[FRIDA_JS_API_REFERENCE.md](FRIDA_JS_API_REFERENCE.md#stalker) for the API
and [`scripts/stalker_trace.js`](../scripts/stalker_trace.js) for a starting
skeleton.

## Notes and Caveats

- **Performance**: Stalker's full instruction-level tracing is expensive —
  scope it to specific modules/threads (see the JS API reference) rather than
  tracing an entire process by default.
- **Stripped binaries**: symbol names may be unavailable; fall back to
  `frida-discover`-reported addresses or static analysis (`rabin2 -s`/`r2`'s
  `aa`/`afl`) to identify functions by behavior/signature instead of name.
- **ASLR/PIE**: runtime addresses reported by Frida are absolute process
  addresses, not static file offsets. Subtract the module's base address
  (`Process.getModuleByName(name).base` in a script, or `frida-ps`/`Module`
  enumeration) to get a relative offset comparable to `rafind2`/`r2` output.
- **macOS code signing**: spawning (`-f`) a signed binary you don't own may
  fail or require the binary to be re-signed with the `get-task-allow`
  entitlement — don't instruct the user to strip another party's signature;
  treat this as a hard platform limitation and fall back to Gadget or inform
  the user it isn't possible.
