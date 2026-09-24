# 38.00 engine update and thread-context candidate

Exact image SHA-256: `f4ddac1044edd0e8cc123f586f7204de8724989b6adcf25b2e34b4855747a5c0`.

## Engine-level update path

The context-travel candidate 0x4832B9A is present at slot 153 in candidate tables 0x119FC3F0, 0x11BBDD10 and 0x12FB3A80. Table starts were inferred using the previously established ProcessEvent entry at slot 28. Enclosing live class identities remain unverified.

The table at 0x11BBDD10 also contains 0x44481DA at slot 94. Routine 0x44481DA iterates the familiar engine context array at +0xFD8. It reads each context's world at +0x2B8, checks a world flag, then calls this->slot153 with engine RCX, context RDX and the preserved floating-point delta in XMM2. On an observed conditional path after that call, it invokes 0x4603DE4 with world RCX, EDX=2 and the same delta in XMM2. The callee has a large update-shaped body; its complete contract is not established.

This extends the previously located connection-management chain to an engine-level context iteration. It does not identify the active FortEngine override or prove that any point in that routine is an appropriate startup hook.

## TLS field and actual OS-thread comparison

At 0x4449603, the code reads an image-global TLS index at RVA 0x16B43A24. It obtains the module's thread-local block through GS:[0x58] and then reads a 32-bit field at TLS block+0xCA0. A global-dependent branch compares that value with 0x10; another branch compares it with 2 and 1. For value 1, the code calls 0x8BF44E and compares its result with a call through import slot 0x1684DE68.

The PE import descriptor and original thunk identify that slot as `KERNEL32.dll!GetCurrentThreadId`. This is verified by the offline checker. The helper at 0x8BF44E returns a global integer after guarded initialization; its full initialization and the identity of that integer remain to be traced. Calling it a game-thread ID without that evidence would be premature.

A later fallback block repeats related checks before taking other branches. These checks occur in a particular later section of the engine-update routine; they are not demonstrated to be an entry precondition for every world update. The numeric TLS values must not be assigned enum names or treated as universal startup authorization merely because they resemble thread/task tags.

## What this enables next

There is now a concrete, image-specific TLS candidate for a read-only callback observation: validate the image and relevant instruction anchors, read the module TLS index, read the current thread's TLS block and report the raw +0xCA0 value without modifying it. The current launcher does not implement that observation yet. A future result would be evidence to compare against normal engine execution, not a permission to forge a TLS value or bypass a check.

The valid execution boundary, required task state, reentrancy rules and active engine override remain unresolved. No engine thread-local state, hook or startup behavior changed in this update.

## Verification

`inspect_network_contracts.py` now validates 38 complete instruction windows, three context-travel table associations, one engine-update table entry and the named OS-thread import, alongside prior driver checks. It reports `EngineTaskTagMeaningVerified=false`, `LiveCallbackValueObserved=false` and `StartupBoundaryApproved=false`. All offline checks passed for the supplied image; no live networking call was attempted.
