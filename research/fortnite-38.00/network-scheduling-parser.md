# 38.00 post-work dispatch and parser failure evidence

Exact executable SHA-256: `f4ddac1044edd0e8cc123f586f7204de8724989b6adcf25b2e34b4855747a5c0`.

## Driver post-work dispatch

Offline table inspection places the pending-removal consumer 0x335924 in slot 110 (+0x370) of NetDriver, IpNetDriver and NetDriverEOSBase. DemoNetDriver instead points to 0x33584A, which directly calls 0x335924 before inspecting additional driver state. These table identities derive from live report 15; slot 110 and its live entry bytes were not included in that report.

The caller at 0x46BA5F2 retrieves an object from this+0x30. On its work path it calls that object's virtual slots 107 (+0x358), 108 (+0x360), and 109 (+0x368), re-reading and null-checking the object after the first two calls. Slots 107 and 109 receive the original XMM1 value. It then re-reads and checks the object again and tail-jumps to slot 110 after restoring its stack. Earlier code follows the pointed object's +0xF8 connection and reads connection+0x18C, consistent with a networking path. This is stronger scheduling evidence than a generic slot-number match, but the enclosing object's exact identity and calling thread/task still require validation.

A raw scan found hundreds of other +0x370 call instructions belonging to unrelated classes. Such a match alone is not evidence of a NetDriver caller. The reproducible checker includes the complete relevant caller and DemoNetDriver override instead of promoting the raw scan results.

The existing WH_GETMESSAGE callback demonstrates one guarded GetOwner call on the named game thread. It does not establish that callback execution has the same engine task state, reentrancy constraints or ordering as this driver work sequence. Do not install a state-changing startup call in that callback based solely on thread identity. No task-tag field or global was guessed or modified.

## Parser failure is represented in object state

The constructor/parser candidate at 0x47CEE60 initializes URL+0x24 to 1, but several normal paths write zero to the same field. Examples:

| Instruction RVA | Operation |
| --- | --- |
| 0x47CF512 | Store 0 to destination+0x24, then reload and test it |
| 0x47CF73A | Store 0 to destination+0x24 before continuing common processing |
| 0x47D0A92 | Store 0 to destination+0x24 before local cleanup and return |
| 0x47D0FD9 | Store 0 to destination+0x24, then branch back into common processing |

The return sequence at 0x47D0ACF loads the original destination pointer into RAX. Thus at least one invalid-input path returns the object pointer normally. Non-null RAX cannot be treated as parse success. The observed +0x24 field is now supported as a parse-validity indicator, rather than merely a constructor-initialized integer.

The invalid-return path releases local temporary allocations before its normal epilogue; it does not call the URL destructor on the destination. Combined with the engine caller that destroys its constructed URL, this supports retaining destination cleanup responsibility on a normal invalid parse return. It does not establish safety after an exception, allocation failure, access violation or interrupted construction. Those cases require separate containment; blindly calling the destructor on an unknown partial object is not validated.

The parser's complete syntax, all enum values, defaults and exception behavior are not proven. A future guard must inspect validity and bounded resulting fields before considering any listen call, retain engine allocation ownership, and never accept a pointer return as its sole success criterion.

## Reproduction and status

The expanded `inspect_network_contracts.py` checks 30 complete instruction windows, four slot-110 entries, four cleanup table mappings and the four previous live table associations against the exact executable. It emits `EngineTaskContextVerified=false` for every slot-110 observation. All checks passed offline.

These are source/research changes, not a new launcher or live test. Hosting remains disabled. The next concrete blocker is establishing a legitimate engine execution boundary and containment for the temporary URL lifecycle before introducing any networking side effect.
