# Function metadata export: CL47722112

The capture export now writes `functions.hpp` alongside `reflection.hpp` and
includes function records and owner storage sizes in `reflection.json` (format 2).
The launcher button is **Export 38.00 properties and functions from a capture**.

Validated against the supplied later capture:

- 631 owner storage sizes, all observed property extents within bounds.
- 495 function/delegate records, including functions with no property fields.
- 2,030 properties retained; no rejected property chains or function records.
- Raw function flags, distinct storage/parameter sizes, and image-relative entry RVAs.

Instruction anchors gate the storage/parameter decoding and native entry read.
Entry pointers must land in an executable section of the matched AMD64 PE image;
non-executable data and outside-image pointers are rejected. Missing native entries
are not fabricated. Zero-entry non-native records retain an explicit null.

The live probe uses the same inspector. A pass remains a read-only observation:
there is no function invocation or game-thread scheduler. Exports keep SDK-ready,
complete-reflection and dispatch-verified flags false. Property parameter flags,
bool masks, nested types and uninitialized owners are still unresolved.

Validation includes two image bases, padded parameter buffers, zero-parameter
functions, malformed sizes, invalid entry locations, mismatched instruction
anchors, malformed PE bounds and C++17 compilation. Captured metadata remains
private; fixtures in source are synthetic.
