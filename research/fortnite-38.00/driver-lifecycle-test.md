# 38.00 experimental driver creation/removal test

The supplied live-test(1).json matched the exact image and observed one FortEngine world context with zero active drivers. GameNetDriver and its fallback both resolved to /Script/OnlineSubsystemUtils.IpNetDriver, with one loaded class match. The world remained the frontend with no NetDriver. Its overall Passed=false is due to 139 unbound native metadata entries, not this configuration inventory.

## Run

Extract the complete new Windows launcher package. Start a fresh matching 38.00 process. In Logs → Game diagnostics select the process and choose **Test 38.00 driver lifecycle**. Upload `driver-lifecycle-test.json`. Close the game after this experiment, including a successful result. It does not enable gameplay or call listen.

## Fixed operation and guards

The managed preflight verifies the executable hash, existing reflection/dispatch checks, one engine context, empty active-driver list, exact GameNetDriver/IpNetDriver definition and matching loaded class/CDO. Internal target addresses remain in the temporary mapping, not the JSON report.

Protocol v5 adds one explicitly requested operation. On the game's callback thread, the DLL repeats thread/TLS and GetOwner checks, compares the complete fixed creation and named-removal bodies, and validates cleanup virtual entries for the exact IpNetDriver table. It rechecks registry memberships, class/name identities, global engine identity, one context and its World, empty active drivers, the exact definition pair and initially clear checked world driver references. No arbitrary function address is accepted.

The named wrapper at RVA 0x1FAFE5E is called once with GameNetDriver as both instance and definition name. Its boolean return is not interpreted as an object pointer. The appended active entry must be the sole entry, retain its definition, be a registered exact IpNetDriver, have the expected instance name and cleanup table, and not be in-progress or pending removal. Only then is 0x1F551F0 called once with that context and name.

Success requires the same context/world, zero active entries afterward, and clear world +0x40/+0x150 and level-collection +0x10/+0x18 driver references. The collection address and count must match the baseline. A returned removal call alone never counts as success. No direct deletion, forced GC, flag override, world assignment or listen call is made. The named-removal path itself performs its normal world/shutdown callbacks.

## Limits

Creation invokes engine listeners: at 0x4830051 RCX is the global delegate-like container at RVA 0x16EA9840, RDX is context.World and R8 is the new driver. Routine 0xBBCF6E iterates that container. This clarifies the earlier shorthand that it was a world/driver notification; it is not a two-argument world method.

Creation and removal can have engine-side effects and leave an object awaiting garbage collection. The report explicitly does not claim physical object destruction or general rollback. A creation exception, false creation result, changed identity, deferred/in-progress state, timeout or failed postcondition is reported as uncertain. The diagnostic does not guess a cleanup target or retry creation. A local per-process guard blocks further diagnostics after an attempted creation; the loaded native module also blocks repeated driver creation. Restart the game after the experiment.

The test remains experimental until a real game report confirms it. Synthetic tests exercise successful ordering, false creation, creation exception, rejected identity, removal exception and failed cleanup verification, plus an actual Windows callback rejecting an invalid target without any lifecycle calls. These tests do not prove real engine behavior.
