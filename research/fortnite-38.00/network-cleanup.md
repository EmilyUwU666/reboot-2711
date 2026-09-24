# 38.00 named-driver cleanup investigation

Exact image: SHA-256 `f4ddac1044edd0e8cc123f586f7204de8724989b6adcf25b2e34b4855747a5c0`. All addresses below are image-relative. This is static evidence, not approval to call engine functions. No gameplay gate changed.

## Removal entry points

The world-oriented wrapper at 0xA64AFBC takes an engine-like RCX, world RDX, and encoded driver name R8D. It resolves the world through the previously observed context array (+0xFD8/+0xFE0, context.World +0x2B8), then tail-jumps to 0x1F551F0 with context RCX and encoded name EDX. The missing-world path calls the still-unvalidated fallback 0x4836B6F.

The context routine traverses the 16-byte active-driver entries at context+0x208, count +0x210. It compares decoded names against driver+0x210 using the already verified name transform. This is the same name field used by creation and lookup.

## Normal removal order

After a name match, when driver byte +0x310 is not 1:

1. Call 0xAA162EC with the context array and matching index. The helper replaces a non-final entry with the last 16-byte entry, decrements count, and calls an allocation-adjustment helper. Array order is not preserved.
2. Perform global-flag-dependent object handling and add an index/serial-shaped reference through a helper using context+0x258. The full semantics of this collection are unresolved.
3. Invoke driver virtual slot 130 with a null world.
4. Invoke driver virtual slot 100, then slot 101.
5. If context.World is non-null, call 0xC56FD12 with that world and the removed driver.
6. Scan engine contexts and their remaining drivers, potentially changing a global flag based on driver+0x891. That flag's semantics remain unresolved.

The world helper at 0xC56FD12 clears matching references at world+0x40 and +0x150, then traverses a world array at +0x1F0/count +0x1F8 with 0x78-byte stride, clearing matching fields at each entry+0x10/+0x18. It is more than a notification; bypassing this helper could leave references behind.

## Deferred branch

When driver byte +0x310 equals 1, the context routine calls 0xC3D7254 and continues scanning without taking the normal remove path. That helper checks driver+0x311 bit 0. If the bit is clear and +0x310 is still 1, it tail-jumps to 0x464D508 with DL=1. The observed tail of that routine sets bit 0 at +0x311. Therefore a returned removal request does not prove context membership has ended or cleanup completed.

The scheduling of the consuming routine and the lifetime of the deferred reference collection remain unresolved. Do not force these fields to zero or treat a timeout as permission to free the object directly.

## Offline cleanup table correlation

The following entries are read from the supplied executable at tables associated with classes in live report 15. The live report did not inspect slots 100/101 or their instruction bytes.

| Class | Slot 100 | Slot 101 |
| --- | --- | --- |
| NetDriver | 0x4641FFA | 0x1C44944 |
| IpNetDriver | 0x4641FFA | 0x4937BF0 |
| DemoNetDriver | 0x4641FFA | 0x1C44944 |
| NetDriverEOSBase | 0x500F4BE | 0x4937BF0 |

The decoded `NetDriver::Shutdown` label lies within 0x4641FFA–0x4642D91, supporting a shutdown interpretation for slot 100. Slot 101's complete contract remains unverified. The IpNetDriver slot-101 implementation itself also calls slot 130 with a null world early in its body. This does not imply the normal sequence is redundant or safe to reorder.

## Broad world shutdown is unsuitable for targeted rollback

Routine 0x482EF38 contains the decoded label `World NetDriver shutdown %s [%s]`. It clears world+0x40 before requesting named removal, then loops over other matching-world active drivers. It skips entries with the pending bit set. It can affect multiple drivers, so it should not be substituted for cleanup of one newly created test driver.

## Validation and next implementation boundary

`inspect_network_contracts.py` now checks 24 complete instruction windows and the offline slot-100/101 entries for four tables. It continues to reject other image hashes and keeps `CallableBindingsVerified=false`. The companion label decoder now includes the two shutdown labels. No live driver was created, removed, or shut down during analysis.

A future guarded transaction must retain the created driver's exact identity and a pre-test context snapshot; request cleanup through the matching engine path; then confirm context removal and world-reference cleanup rather than equating a function return with completion. It must preserve pre-existing drivers and distinguish deferred cleanup from failure. This is a requirement for the runtime implementation, not an implemented transaction.

The next unresolved work is the scheduling and relevant engine task context of the now-located pending-removal consumer, followed by parser failure behavior. Another unchanged GetOwner capture would not answer those questions.

## Pending-removal consumer located

Routine 0x335924 saves driver+0x310, sets it to 1 around inner work, restores the saved value, and tests pending bit 0 at +0x311. If pending and World (+0x1B0) is non-null, it calls the named-removal world wrapper 0xA64AFBC with the driver's encoded name. It then clears the pending bit. If World is null, it may log and clears the bit without that removal call. This establishes a consumer, but neither its engine scheduling nor its task tag has been established. A cleared pending bit alone is not proof of successful cleanup: context membership and world references must still be checked.

The +0x310 pattern supports an in-progress/reentrancy interpretation for this driver path. It is not a global engine task tag. The consumer must not be called arbitrarily to force pending work, and unrelated objects with coincidentally identical offsets must not be treated as drivers.
