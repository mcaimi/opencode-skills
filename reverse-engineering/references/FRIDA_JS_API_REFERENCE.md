# Frida JavaScript API Reference

This reference covers the Frida JavaScript API for writing instrumentation
scripts (agents) loaded via `frida -l <script>`, `frida-trace`'s generated
handlers, or embedded in a Gadget config. For the CLI tools that load these
scripts, see [FRIDA_REFERENCE.md](FRIDA_REFERENCE.md). Every API below is
either read-only/observational or state-changing — state-changing use is
flagged against the
[Destructive/Impactful Dynamic Operations Gate](../SKILL.md#destructiveimpactful-dynamic-operations-gate)
in `SKILL.md`.

Use a bundled template in [`../scripts/`](../scripts/) as a starting point
before writing an agent from scratch — they cover the three most common
tasks (call tracing, Stalker-based code-flow tracing, memory dumping) with
the message-pump/cleanup boilerplate already wired up.

## Interceptor

Hooks a specific address/export, running JS before (`onEnter`) and/or after
(`onLeave`) the original function executes.

```js
// Passive: observe only — needs just the Dynamic Analysis Consent Gate
Interceptor.attach(Module.getExportByName(null, 'open'), {
  onEnter(args) {
    this.path = args[0].readUtf8String();
  },
  onLeave(retval) {
    send({ type: 'call', func: 'open', path: this.path, retval: retval.toInt32() });
  }
});
```

```js
// Behavior-modifying: needs the Destructive/Impactful Dynamic Operations Gate
Interceptor.attach(Module.getExportByName(null, 'isDebuggerPresent'), {
  onLeave(retval) {
    retval.replace(0); // changes what the caller sees — this is a modification
  }
});

// Interceptor.replace swaps the function body entirely — always modifying
Interceptor.replace(targetAddr, new NativeCallback(() => 0, 'int', []));
```

`onEnter`/`onLeave` callbacks should be wrapped in `try { } catch (e) { send({type: 'error', error: e.message}); }`
so a hook bug doesn't crash the target process.

## Stalker

Follows a thread's execution instruction-by-instruction or block-by-block,
letting you reconstruct code flow or build a full execution trace.

```js
const tid = Process.getCurrentThreadId();

Stalker.follow(tid, {
  events: { call: true, ret: false, exec: false },
  onReceive(events) {
    const calls = Stalker.parse(events, { annotate: true, stringify: false });
    for (const c of calls) {
      send({ type: 'stalker-call', from: c[1], to: c[2] });
    }
  },
  transform(iterator) {
    let instruction;
    while ((instruction = iterator.next()) !== null) {
      // Optionally filter to specific modules to control cost, e.g.:
      // if (!Process.getModuleByAddress(instruction.address).name.includes('target')) { iterator.keep(); continue; }
      iterator.keep();
    }
  }
});

// Always clean up when done, especially before the script unloads
// Stalker.unfollow(tid);
```

Scope Stalker to a specific thread and, inside `transform`, to specific
modules — full-process instruction tracing is expensive and generates a lot
of noise. Use `events.call`-only tracing for a lightweight call graph, and
full instruction-level `transform` only when you need true code-flow
reconstruction.

## Memory

```js
// Read-only — no gate beyond the Consent Gate
const bytes = Memory.readByteArray(ptr('0x1000'), 256);

// Scan a memory range for a byte pattern
Memory.scan(baseAddr, size, '48 65 6c 6c 6f', {
  onMatch(address, size) {
    send({ type: 'scan-hit', address: address.toString() });
  },
  onComplete() {}
});
```

```js
// Writes — needs the Destructive/Impactful Dynamic Operations Gate
Memory.protect(addr, size, 'rwx');
Memory.writeByteArray(addr, newBytes);
```

Any `Memory.write*` call, or `Memory.protect` followed by a write, modifies
the live process and must be treated as a behavior-modifying operation.

## Process / Module

Used to resolve addresses for `Interceptor`/`Stalker`/`Memory` calls, and to
map a runtime address back to a module-relative offset comparable to static
`rafind2`/`r2` output.

```js
Process.enumerateModules().forEach(m => {
  send({ type: 'module', name: m.name, base: m.base.toString(), size: m.size });
});

const mod = Process.getModuleByName('libtarget.so');
mod.enumerateExports().forEach(e => {
  send({ type: 'export', name: e.name, address: e.address.toString() });
});

// Relative offset = absolute address - module base (compare against a static file offset)
const relOffset = someAddress.sub(mod.base);
```

## The `send()`/`recv()` convention

Agents communicate with the host process via `send(payload, data)` (JS →
host) and `recv(type, callback)` (host → JS). For this skill, templates emit
one JSON object per `send()` call (JSON-lines) with a `type` field
distinguishing event kinds (`call`, `stalker-call`, `module`, `error`, etc.).
This is the format [`scripts/frida_jsonl_to_md.py`](../scripts/frida_jsonl_to_md.py)
expects on stdin — pipe `frida`'s stdout/stderr output accordingly, e.g.:

```bash
frida -p 1234 -l scripts/call_trace_logger.js 2>/dev/null | python3 scripts/frida_jsonl_to_md.py -
```

## Worked Examples

**Passive call logger** — see [`scripts/call_trace_logger.js`](../scripts/call_trace_logger.js)
for the full annotated template; the core pattern is the `Interceptor.attach`
block shown above, repeated per target function.

**Stalker basic-block tracer** — see [`scripts/stalker_trace.js`](../scripts/stalker_trace.js)
for the full annotated template; the core pattern is the `Stalker.follow`
block shown above with `events.call: true` for a lightweight call graph.

**Memory dump on hook** — combine `Interceptor.attach`'s `onEnter` with
`Memory.readByteArray` to capture a buffer argument at the moment a function
is called:

```js
Interceptor.attach(targetAddr, {
  onEnter(args) {
    const buf = Memory.readByteArray(args[1], args[2].toInt32());
    send({ type: 'memory-dump', at: 'onEnter' }, buf);
  }
});
```

See [`scripts/memory_dump.js`](../scripts/memory_dump.js) for a standalone
module/range dump that doesn't require a hook trigger.

## Notes and Caveats

- **ObjC/Swift bridging (macOS)**: `ObjC.classes`/`ObjC.available` let you
  hook Objective-C methods by selector; Swift symbols are frequently mangled
  and may need `Module.enumerateSymbols()` plus demangling to locate.
- **Exception hygiene**: always wrap hook bodies in `try/catch` — an
  uncaught JS exception inside `onEnter`/`onLeave` can crash or hang the
  instrumented thread.
- **Cleanup**: call `Stalker.unfollow()` for any thread you followed, and
  avoid leaving `Interceptor.replace()` hooks installed past the end of the
  analysis session if the process will continue running afterward — restore
  original behavior when the task doesn't call for a persistent patch.
- **Determinism**: dynamic analysis only reveals code paths actually
  exercised during the session — absence of a call/behavior in the trace
  does not mean the code path doesn't exist; state this caveat in reports.
