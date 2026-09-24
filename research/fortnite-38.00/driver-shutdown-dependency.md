# 38.00 driver shutdown dependency

Live report 3: creation succeeded; named removal removed the active entry (fresh count 0) but raised read AV at game RVA 0x9FA51B3, target 0x80. The instruction is `mov eax,[rcx+0x80]`; RCX was therefore null at the fault. Context removal is not completed shutdown.

The direct caller is the observed NetDriver shutdown implementation: 0x464289B loads driver+0x290 into RCX; 0x46428A2 calls 0x9FA51AA unconditionally. This establishes the missing field, rather than an incorrect world/context-array offset.

The IpNetDriver init path at 0x49342E1 invokes base initialization at 0x155E5EC. At 0x155E801–0x155E80D that path calls driver virtual slot 87. The supplied IpNetDriver table maps slot 87 to 0x9E674C2. That method creates a UObject through 0x9E68A60, writes it into driver+0x290 and performs its registrations. The helper uses the engine UObject constructor at 0x27D9FC and the class getter at 0x1667B9A (cached class pointer image+0x16E89D60). These are static observations; they do not establish complete driver initialization or socket readiness.

The experimental lifecycle now invokes the exact slot-87 implementation once after creating and validating the test driver, only if +0x290 is null. It verifies the full initializer body and relevant helper anchors before creation, requires the expected virtual entry, and then checks that the new field refers to a registered non-default object of the helper's cached class. It rechecks the original driver/context identity before named removal. It does not write a fake pointer, bypass shutdown, start listen, or call the full socket-init path.

Protocol v7 reports InitializeCalls and DependencyReady, and fault stage Dependency initialization when applicable. Initializer exceptions or an invalid resulting dependency stop the test before removal; game restart is required. The native sequence tests cover both cases and confirm that removal is not attempted. A later cleanup dependency may still fail; fault capture remains enabled.

Use a fresh game instance and the new complete package. Run Logs → Game diagnostics → Test 38.00 driver lifecycle, upload driver-lifecycle-test.json, and close the game afterward. The change is a candidate correction to the incomplete experimental lifecycle, not a live-verified gameplay fix.
