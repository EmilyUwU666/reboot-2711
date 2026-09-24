# 38.00 networking contract evidence

Applies only to SHA-256 `f4ddac1044edd0e8cc123f586f7204de8724989b6adcf25b2e34b4855747a5c0`.

## Live report 15

The supplied report retained successful guarded GetOwner dispatch, stable boundary counters and a live game. It observed one engine world context, referencing the front-end world with a null NetDriver. No networking call was attempted. Native metadata still contains 139 excluded entries; this is not full SDK or gameplay validation.

The class-default identities establish these table associations for that observation:

| Class | Table RVA | Getter slot 50 | Listen slot 93 | Assignment slot 130 |
| --- | --- | --- | --- | --- |
| NetDriver | 0x11CA8470 | 0xC306F9A | 0x4655228 | 0xFC3134 |
| IpNetDriver | 0x11E085C0 | 0xC306F9A | 0x49354B8 | 0xFC3134 |
| DemoNetDriver | 0x11B9D340 | 0xC306F9A | 0xC30583C | 0xFC2ECE |
| NetDriverEOSBase | 0x1220CC80 | 0xC306F9A | 0x500F0CA | 0xFC3134 |

DemoNetDriver's distinct entries were not recognized by the live probe. Offline inspection now confirms that its reported pointers equal the supplied executable's table. That does not validate those methods' live instruction bytes or calling contracts. Do not add them to the callable allowlist on this basis.

## Listen argument forwarding

At 0x49354B8, seven register pushes and a 0xF0-byte allocation move RSP down by 0x128. The load at 0x49354D2 from adjusted RSP+0x150 therefore reads entry RSP+0x28: the fifth Windows x64 argument, not the fourth.

The virtual call at 0x49354FE (slot 91) receives:

| Callee location | Value |
| --- | --- |
| RCX | Original driver pointer |
| EDX | Zero |
| R8 | Original RDX |
| R9 | Original R8 |
| Caller RSP+0x20 | Original R9B |
| Caller RSP+0x28 | Original fifth argument |

The return low byte controls success. On success slot 95 is called and a socket-like object's virtual slot 7 supplies the value written at original R8+0x20. On failure, the fifth argument is read as a string-like data pointer with a count at +8. Together with decoded labels, this supports the provisional shape `bool(driver, notify-like pointer, URL-like reference, bool, error-string-like reference)`. These semantic names remain inferences; no callable C++ declaration is generated.

The URL formatting helper at 0x155CABE reads a collection pointer at +0x48 and count at +0x50, with a 16-byte element stride, and appends `?` before its entries. This strengthens the options-array interpretation. The full URL layout, constructor, destructor, allocator and validity state remain unverified; a guessed zero-filled URL must not be passed to the engine.

## Driver creation and name order

The world wrapper at 0xA6B0BC0 searches the engine context array at +0xFD8/+0xFE0 by context.World (+0x2B8), then tail-jumps to 0x1FAFE5E. Its missing-context path calls 0x4836B6F; that fallback is not validated.

At 0x1FAFE5E, original R8D is used to search the context's collection at +0x208. Helper 0x482F26A traverses 16-byte entries and compares the supplied decoded name with the pointed driver's encoded field at +0x210. This supports identifying R8D as a driver-instance name.

The wrapper then passes original R9D as R8D and original R8D as R9D to 0x482F38E. That function searches 16-byte engine definition entries at +0xF50/+0xF58 using its R8D, supporting definition-name first and instance-name second at the lower level. It converts a name at definition+4 to a string before further construction work.

Crucially, the wrapper tests the lower-level returned pointer and returns a boolean in AL. A port must not interpret the wrapper's return as a NetDriver pointer. Existing-name lookup takes a false-return path rather than returning the existing pointer.

## Reproduction and remaining work

Run `python inspect_network_contracts.py /path/to/38.00.exe --live-report /path/to/dispatch-test.json` with Capstone installed. It rejects other image hashes, maps RVAs through PE sections, checks complete instruction decoding for selected evidence windows, checks all four on-disk vtables and optionally correlates supplied live JSON. The companion JSON contains only selected instructions and relative addresses, no user memory dump or executable.

Still required before enabling hosting: validate construction ownership and configuration, complete URL/error-string lifetime rules, validate engine task context, and implement a bounded startup/cleanup path on an appropriate gameplay world. No launcher behavior, runtime gate, backend, native hook or networking call is changed by this research update. No repeat live capture is needed for this offline step.
