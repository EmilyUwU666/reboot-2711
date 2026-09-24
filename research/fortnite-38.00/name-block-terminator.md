# Closed name-block end markers, CL47722112

The 2026-09-23 21:20 UTC report repeats an identical boundary failure on all three
fresh reads: closed block 214, offset 0x1FFD8, header 0xD0CC, decoded length 300,
40 bytes available versus 302 required. Its startup observation matched the
profile, found no active early patcher, and confirmed SkipPatchCheck was present.
No callback or Unreal function was attempted. This shows the prior early screen
was no longer active, but does not establish lobby access or gameplay readiness.

Inspection of the supplied executable establishes a missing decoder rule.
AllocateNewBlock at RVA 0xD1A6E checks whether at least ten bytes remain at the
old cursor. If so, instructions 0xD1A8C–0xD1AA3 write an encoded zero-length header
(old byte OR 0x9BC0) and clear the following eight bytes. It then advances the
block index and resets the cursor. Bytes after this marker are not cleared.
The native enumeration routine at 0xB334088 explicitly stops at a zero-length
entry when both following 32-bit words are zero (0xB3340D5–0xB3340DF).

The old reader instead emitted a numbered None_-1 entry for the marker and
continued scanning the unused tail. A nonzero tail can eventually look like a
name longer than the remaining bytes. This fits the new failure pattern; the
JSON does not include block 214's preceding bytes, so its precise marker location
has not independently been observed.

The corrected reader stops only on the verified marker in a closed block. It
does not skip arbitrary oversized names. A marker inside the current block,
truncated entries and nonzero numbered records retain validation. Live and
capture readers additionally verify the allocator's 45 instruction bytes at
RVA 0xD1A76 before relying on the rule. The bounded fresh-read retries and failure
reports from the previous build remain enabled.

Regression tests place a valid marker ahead of poisoned trailing bytes, including
the reported 0xD0CC header near the end; verify the next block is decoded; ensure
the marker is not emitted as a name; and reject malformed/current-block data.
A nonzero numbered record is still treated as a record rather than a marker.

The earlier supplied later capture now yields 153,407 plain and 78 numbered names,
removing 22 phantom marker entries from the prior count of 100 numbered names.
The same 23,051 object slots, 633 owners, 2,032 properties and 497 functions still
validate with no rejected slots/chains/bindings. The captured allocator instruction
profile matches. A fresh user live test is needed to establish whether the newer
startup state now passes this stage and what remains before gameplay.

Materialize emilyfn-name-block-terminator.patch after emilyfn-name-read-recovery.patch.
