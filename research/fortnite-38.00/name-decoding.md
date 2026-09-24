# CL47722112 name decoding (2026-09-23)

The supplied live capture validates as a 2,009,481,108-byte full minidump:
2,514 memory ranges, 106 modules and 29 threads. Game base is 0x4B0000.
The name pool initialization flag (image RVA 0x16C1C5A8) is set. Pool RVA
0x16C1C5C0 has current block 31 and cursor 23,178.

C# export of this actual capture produced 143,500 plain and 79 numbered names.
Every numbered reference resolved to a plain entry. Some numbered allocations
have two alignment padding bytes; requiring all numbered entries to have one
alignment was disproven by the capture and is not enforced.

Entry length is (header >> 6) XOR 0x26F. Header bit 0 selects wide text.
The payload state starts with character count, and each byte updates it with
state = state * 0xFFFFDE61 + 0xFE93E844 (32-bit wrap); the byte is XORed with
low8(state + 0x4A). Decoder routine RVA is 0x3A00362, called by RVA 0x28D86.
Numbered records contain an encoded suffix at +2 and encoded base index at +6.
Index decoding and the suffix special cases follow those instructions.
The narrow conversion reproduces signed-byte widening from the executable.
Wide decoding is implemented from instructions but lacks an independently
identified captured test vector.

The importer checks image size and two instruction anchors, plus minidump
bounds, memory ranges, pool bounds and None sentinel. These are decoding
compatibility checks, not a cryptographic verification of the whole image.

UObject registry, class/property layouts, function dispatch and server hooks
remain UNVERIFIED. Searching expected core name IDs at the observed UObject
name field (+0x20) did not establish a viable registry. The capture's two-second
startup delay may be too early, but this is a hypothesis, not a proven cause.
The launcher now allows 15/30/60/120 seconds, default 30. Waiting longer does
not guarantee reflection initialization. Manual capture of an already running
game remains available.

The launcher exports names.hpp plus a report explicitly marking SdkReady=false.
It does not claim full SDK generation or enable 38.00 gameplay. No original
executable, full memory, or complete runtime name list is committed.
