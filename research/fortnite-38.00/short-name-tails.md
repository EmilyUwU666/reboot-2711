# Closed name blocks with fewer than ten tail bytes

The 2026-09-23 21:33 UTC report from the same game process passes the earlier
block-214 location and fails identically across three fresh reads at closed
block 272, offset 0x1FFF8. Header 0xE45E describes a 512-byte allocation but only
eight bytes remain. SkipPatchCheck is still observed and the early patcher is
inactive. No native callback or Unreal function was attempted.

The verified AllocateNewBlock instructions at RVA 0xD1A76 add ten to the current
cursor and compare against 0x20000. The branch at 0xD1A82 skips writing the end
marker when it will not fit. This is the short-tail case omitted from the prior
end-marker fix. Pool offsets are two-byte aligned, so possible nonempty short
remainders are two, four, six and eight bytes.

The parser now stops when all three conditions hold: the block is closed, fewer
than ten bytes remain, and the candidate allocation exceeds those bytes. It
still decodes a valid small entry that fits. It does not discard all short-tail
entries, relax current-block bounds, or accept larger overflows without an
explicit verified end marker. The existing allocation instruction profile gate
covers the ten-byte comparison and its branch.

Tests synthesize complete valid prefixes ending at every short remainder and
exercise the reported header, numbered-looking tails and zero headers with dirty
trailing bytes. They check continuation into the next block, absence of a phantom
tail name, rejection of current-block truncation, rejection with ten/twelve/forty
bytes remaining, and preservation of a valid eight-byte final entry.

The earlier full capture still produces 153,407 plain and 78 numbered names,
23,051 object slots, 633 owners, 2,032 properties and 497 functions with no rejected
entries/chains/bindings. The new live report provides header and location but not
the preceding block bytes; the next test must confirm this case clears in the
user's running process. This change does not establish gameplay readiness.

Materialize emilyfn-short-name-tails.patch after emilyfn-name-block-terminator.patch.
