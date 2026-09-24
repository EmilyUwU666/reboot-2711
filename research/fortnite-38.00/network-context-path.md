# 38.00 connection-work context path

Exact image SHA-256: `f4ddac1044edd0e8cc123f586f7204de8724989b6adcf25b2e34b4855747a5c0`.

## What the previous work sequence belongs to

The function 0x46BA5F2 is stored at table 0x11CD07B0, slot 86 (+0x2B0). The constructor-like routine 0xA9EDE75 installs that table, zeros fields +0x30/+0x38, constructs a URL at object+0x40 using 0xB2FC82, and zeros the string-shaped field at +0xB0. A destruction routine at 0x18E770E installs the same table and releases the embedded string/array fields corresponding to that URL and the +0xB0 string. This links the work function to an object with a driver-like member at +0x30 and an embedded URL, rather than to the engine object itself.

The engine/context routine at 0x4832B9A saves its second argument as the context, accesses context.World at +0x2B8, and later fetches context+0x188. At 0x4832C6F it calls that object's slot 86 with the preserved floating-point delta argument. Afterwards it re-reads context+0x188 and examines the object's string count at +0xB8. This connects the table's slot to a context-side connection-management path.

| Stage | Observed relationship |
| --- | --- |
| Context routine | Reads object at context+0x188 |
| Object work | Calls virtual slot 86 |
| Candidate table | Slot 86 resolves to 0x46BA5F2 |
| Driver member | Work routine reads object+0x30 |
| Driver work | Slots 107, 108, 109, then 110 |
| Post-work | Known driver tables resolve slot 110 to the pending-removal consumer, with a DemoNetDriver wrapper |

These are static relationships. The exact live class at context+0x188 has not been checked, and a null field would mean this route is inactive. The object shape and use of connection state support a pending-connection interpretation, not a confirmed class identity. In particular, context+0x188 must not be confused with context.World+0x2B8 or the context's active-driver array+0x208.

## Consequence for the port

The previous scheduling evidence shows how one connection-related path reaches the cleanup consumer. It does not prove that this is the normal server-world driver tick or a valid server-startup hook. Calling this work function on the lobby engine/world, or installing a hook merely because its slot ultimately reaches NetDriver, would use the wrong object contract.

No engine task-tag setup was established in this chain. The context routine was found in three on-disk pointer locations (0x119FC8B8, 0x11BBE1D8, 0x12FB3F48); their enclosing class identities and callers are not yet resolved. An E8 relative-call scan found no direct byte-pattern references to its entry. That negative scan does not rule out indirect calls or other reference forms.

The existing diagnostic's successful GetOwner result remains valid, but does not approve networking calls from its message callback. Server startup and lifecycle calls remain disabled.

## Reproducibility

The checker now includes the complete constructor and destructor routines and the context routine's prefix through its slot-86 call and follow-up object read. It checks the candidate table entry and emits `LiveObjectClassVerified=false`, `ServerStartupBoundaryVerified=false`, and `EngineTaskContextVerified=false`. All 33 instruction windows, the candidate connection table entry, existing driver table checks and supplied live table associations passed offline.

Next work must resolve an actual engine/world execution boundary and its task-state requirements, rather than treating the pending-connection route as sufficient. This investigation requires no repeat of the unchanged live capture.
