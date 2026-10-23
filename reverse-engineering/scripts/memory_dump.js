/*
 * memory_dump.js — read-only module/range memory dump template.
 *
 * Usage:
 *   frida -p <pid> -l scripts/memory_dump.js
 *   frida -f /path/to/binary -l scripts/memory_dump.js
 *
 * Edit MODULE_NAME (or RANGE_BASE/RANGE_SIZE) below to select what to dump.
 * Read-only by construction (Memory.readByteArray only — no writes), so it
 * needs only the Dynamic Analysis Consent Gate, not the
 * Destructive/Impactful Operations Gate, in SKILL.md.
 *
 * Emits one 'memory-dump' message per chunk via send(payload, data), where
 * `data` is the raw ArrayBuffer (base64-encoded automatically by Frida's
 * message transport). Pipe through scripts/frida_jsonl_to_md.py for a
 * summary table (it will report chunk metadata; the binary payload itself
 * should be redirected/saved separately if you need the raw bytes).
 */

// Edit: dump a named module in full ...
const MODULE_NAME = null; // e.g. 'libtarget.so'
// ... or an explicit address range instead (used only if MODULE_NAME is null)
const RANGE_BASE = null; // e.g. '0x100000000'
const RANGE_SIZE = 0;

const CHUNK_SIZE = 0x10000;

function dumpRange(base, size, label) {
  let offset = 0;
  while (offset < size) {
    const len = Math.min(CHUNK_SIZE, size - offset);
    try {
      const buf = Memory.readByteArray(base.add(offset), len);
      send({ type: 'memory-dump', label, offset, length: len }, buf);
    } catch (e) {
      send({ type: 'error', label, offset, error: e.message });
    }
    offset += len;
  }
}

if (MODULE_NAME !== null) {
  const mod = Process.getModuleByName(MODULE_NAME);
  dumpRange(mod.base, mod.size, mod.name);
} else if (RANGE_BASE !== null && RANGE_SIZE > 0) {
  dumpRange(ptr(RANGE_BASE), RANGE_SIZE, RANGE_BASE);
} else {
  send({ type: 'error', error: 'set MODULE_NAME or RANGE_BASE/RANGE_SIZE before running' });
}

send({ type: 'ready' });
