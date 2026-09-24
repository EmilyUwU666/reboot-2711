# Driver cleanup exception capture

Two supplied live reports show a successful creation/identity check followed by removal access violation 0xC0000005, with the game alive. The failure reproduced in different processes. No listen call was made. The old AfterCount=1 was the pre-removal observation, not a confirmed post-exception count.

Protocol v6 captures creation/removal exception stage, game-relative fault instruction address, read/write/execute type, and a near-null or game-relative target offset. Other target addresses are withheld. Faults outside the game image have no game RVA; no external-module identity is inferred. No registers, stack contents or user memory are exported.

After a removal exception, a bounded read attempts to obtain the current active-driver count. Unknown remains null; even zero does not prove successful cleanup. Exception handling still exits the test with failure and blocks retries; it does not resume the failing instruction, retry removal or free the object.

Windows CI tests cover synthetic exception records (image bounds, null offsets, address redaction and missing parameters) and a real PAGE_NOACCESS read caught by the same SEH filter. Existing callback tests require no fault location on rejected targets.

Use a fresh game instance and the new complete launcher package: Logs → Game diagnostics → Test 38.00 driver lifecycle. Upload driver-lifecycle-test.json and close the game afterward. This build adds diagnostic evidence; it does not fix the underlying cleanup failure or enable gameplay.
