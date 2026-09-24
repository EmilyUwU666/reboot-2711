# 38.00 driver configuration inventory

The URL lifecycle live report passed one construction/destruction with validity 1, port 7777, and the game alive. This next build collects driver prerequisites without creating or listening on a driver.

Use Logs → Game diagnostics → Test 38.00 live bindings. Upload `live-test.json`. The new section is `WorldReadiness.DriverConfiguration`; dispatch and URL reports also include it in their binding evidence.

The exact CL47722112 instruction profiles gate engine definition array +0xF50 (16-byte entries: encoded name, class path, fallback class path), and context active drivers +0x208 (16-byte driver/definition pairs). Engine identity uses the existing exact FortEngine context validation. Array counts are bounded, active driver internal indices are checked against the captured registry, and definition pointers must be aligned members of the configured array. Missing names/classes remain explicitly unresolved.

These cached reads are not an atomic snapshot. A loaded class does not establish constructibility or successful startup. No create, destroy, listen, or world-assignment function is called. GameplayReady remains false.

Synthetic Windows tests cover class availability, active membership, stale indices, invalid definition pointers, absent names, empty/oversized arrays and changed instruction bytes. The user must run the new live inventory before its real configuration can be assessed.
