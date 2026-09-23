# Runtime object registry, 38.00 CL47722112

The user's dispatch report on 2026-09-23 confirms callback delivery on the named
GameThread, with the game still alive. It does not confirm a function call:
Default__ActorComponent was missing, so GetOwner was skipped.

The previous 32-byte table at RVA 0x16CFACD8 is a secondary lookup structure.
It contains 23,050 slots in the supplied later capture, including one invalid
entry. It must not be treated as the complete runtime object registry.

Instruction inspection identified the actual registry:

| Value | Location / decoding |
| --- | --- |
| Chunk pointer array | QWORD(image + 0x16CFAF80) XOR 0xFFFFFFFF40F0F3B4 |
| Slot count | DWORD(image + 0x16CFAF94) XOR 0xFF3B3CEB |
| Chunk size | 65,536 items |
| Item address | chunks[index >> 16] + (index & 65535) * 24 |
| Packed object | ((QWORD(item) & 0x3FFF00000000) OR (DWORD(item + 8) XOR 0xCC9E16DB)) << 3 |
| Internal index | DWORD(object + 0x14) XOR 0x753838AB |

The index/chunk path is checked against instruction bytes at RVA 0x6213;
packed-pointer decoding is checked at RVA 0x23EEE. The object internal index
must equal its registry slot. Null packed pointers count as empty slots, while
missing chunks, unreadable objects and index mismatches are rejections.

The supplied later capture gives 23,051 objects, zero empty slots and zero
rejections. Reflection export now contains 633 populated owners, 2,032 properties
and 497 function records (including delegate kinds), with no rejected chains or
function metadata. Two distinct StopSimulating functions were absent from the
old lookup table. This does not establish complete runtime initialization.

There is still no Default__ActorComponent in that capture. The next live test
must report its actual availability; the registry fix alone does not establish
function dispatch or gameplay support.

The launcher reuses one verified registry snapshot for reflection and target
selection. Live boundary checks now compare the encoded runtime count/chunk
pointer as well as name-pool counters. These are boundary checks, not a lock or
proof of an atomic snapshot. The callback independently verifies registry
membership for the class, receiver and function before applying the existing
fixed GetOwner guards. No object construction or substitute receiver is added.

Tests cover packed pointers in both address ranges, the 65,535/65,536 chunk
boundary, empty slots, index mismatch, missing chunks, count bounds, incorrect
instruction bytes, ambiguous receivers and native membership failure paths.
The Windows workflow also reruns cross-process callback, timeout, capture and
launcher/backend regression fixtures. Synthetic tests do not execute Fortnite.

Materialize emilyfn-runtime-registry.patch after emilyfn-thread-dispatch.patch.
Reflection reports use format 3. Live/dispatch evidence adds RegistrySlots,
EmptyRegistrySlots and RejectedRegistrySlots. Full SDK, Unreal task-tag
verification, server hooks and 38.00 gameplay remain unfinished.
