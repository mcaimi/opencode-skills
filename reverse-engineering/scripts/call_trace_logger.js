/*
 * call_trace_logger.js — passive Interceptor-based call tracer template.
 *
 * Usage:
 *   frida -p <pid> -l scripts/call_trace_logger.js
 *   frida -f /path/to/binary -l scripts/call_trace_logger.js
 *
 * Edit TARGETS below to list the module/function pairs to hook. This
 * template is passive/observational only (onEnter/onLeave log args and the
 * return value via send() — nothing is modified), so it needs only the
 * Dynamic Analysis Consent Gate, not the Destructive/Impactful Operations
 * Gate, in SKILL.md.
 *
 * Output is JSON-lines on stdout, one object per call, consumable by:
 *   frida ... -l scripts/call_trace_logger.js 2>/dev/null | python3 scripts/frida_jsonl_to_md.py -
 */

// Edit this list: { module: null for any module, or 'libc.so'/'libSystem.B.dylib' etc., name: 'exported symbol' }
const TARGETS = [
  { module: null, name: 'open' },
];

TARGETS.forEach(({ module, name }) => {
  const addr = Module.getExportByName(module, name);
  if (addr === null) {
    send({ type: 'error', error: `export not found: ${module || '*'}!${name}` });
    return;
  }

  Interceptor.attach(addr, {
    onEnter(args) {
      try {
        this.startTs = Date.now();
        this.func = name;
        // Add argument capture here as needed for the target function's signature, e.g.:
        // this.arg0 = args[0].readUtf8String();
      } catch (e) {
        send({ type: 'error', func: name, phase: 'onEnter', error: e.message });
      }
    },
    onLeave(retval) {
      try {
        send({
          type: 'call',
          func: this.func,
          timestamp: this.startTs,
          retval: retval.toInt32(),
        });
      } catch (e) {
        send({ type: 'error', func: name, phase: 'onLeave', error: e.message });
      }
    },
  });
});

send({ type: 'ready', targets: TARGETS.length });
