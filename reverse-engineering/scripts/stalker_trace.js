/*
 * stalker_trace.js — Stalker-based code-flow tracer skeleton.
 *
 * Usage:
 *   frida -p <pid> -l scripts/stalker_trace.js
 *   frida -f /path/to/binary -l scripts/stalker_trace.js
 *
 * This is a skeleton, not a turnkey tool — Stalker configuration (which
 * thread, which modules, call-only vs. full instruction tracing) is
 * inherently per-task. Edit MODULE_FILTER and the `events` block below
 * before running. Passive by construction (reads/re-emits code, never
 * writes process memory), so it needs only the Dynamic Analysis Consent
 * Gate, not the Destructive/Impactful Operations Gate, in SKILL.md.
 *
 * Output is JSON-lines on stdout, consumable by:
 *   frida ... -l scripts/stalker_trace.js 2>/dev/null | python3 scripts/frida_jsonl_to_md.py -
 */

// Edit: restrict tracing to a specific module name to control cost, or set
// to null to trace whatever code the followed thread executes.
const MODULE_FILTER = null; // e.g. 'libtarget.so'

const tid = Process.getCurrentThreadId();

function inScope(address) {
  if (MODULE_FILTER === null) return true;
  const mod = Process.findModuleByAddress(address);
  return mod !== null && mod.name === MODULE_FILTER;
}

Stalker.follow(tid, {
  // Lightweight call-graph tracing by default. Set exec: true for full
  // instruction-level tracing (expensive — expect significant slowdown).
  events: { call: true, ret: false, exec: false },

  onReceive(events) {
    try {
      const parsed = Stalker.parse(events, { annotate: true, stringify: false });
      parsed.forEach(entry => {
        send({ type: 'stalker-call', from: entry[1].toString(), to: entry[2].toString() });
      });
    } catch (e) {
      send({ type: 'error', phase: 'onReceive', error: e.message });
    }
  },

  transform(iterator) {
    let instruction;
    while ((instruction = iterator.next()) !== null) {
      if (inScope(instruction.address)) {
        // Add per-instruction instrumentation here if needed, e.g.:
        // iterator.putCallout(() => send({ type: 'bb', address: instruction.address.toString() }));
      }
      iterator.keep();
    }
  },
});

send({ type: 'ready', tid, moduleFilter: MODULE_FILTER });

// Remember to unfollow when the analysis session ends:
// Stalker.unfollow(tid);
