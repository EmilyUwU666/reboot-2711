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

## Follow-up: URL lifetime and driver registration

An engine caller provides stronger lifetime evidence. In 0xC5A6372–0xC5A668F, a base temporary at stack+0xB8 is initialized through 0xB2FC82 with a null second argument, then configured through another routine. A second temporary at stack+0x40 is passed to 0x47CEE60 with that base, a text pointer and enum-like value 1. The second temporary is formatted through 0x155CABE and destroyed through 0x1B609FA. The base is subsequently destroyed through the same routine. The two stack locations are 0x78 apart; this is not itself proof of exact object size.

The constructor at 0xB2FC82 and parser prefix at 0x47CEE60 initialize five string-shaped fields at +0x00, +0x10, +0x28, +0x38, +0x58, an options array at +0x48, port at +0x20, and a candidate validity integer at +0x24 (initialized to 1). The furthest observed field is capacity at +0x64, giving a 0x68-byte candidate layout. These constructors copy global defaults and allocate through engine routines. Their behavior is materially different from zeroing the structure.

The destructor candidate at 0x1B609FA frees +0x58, destroys each options element through 0x8D2FFEF, frees the options allocation, then frees +0x38, +0x28, +0x10 and +0x00. The options-element helper advances by 16 bytes and frees each non-null first pointer. These paths converge on 0x8D2505C. That address's full allocator contract and exception behavior are not yet established; do not mix engine allocations with host free/delete or blindly destroy partially constructed buffers.

`network-layout-candidates.h` captures these storage shapes with explicit integer address fields and compile-time offset assertions. It deliberately supplies no function pointer typedefs, RAII owner, live address conversion or callable operations. The header passes C++17 compilation with warnings treated as errors on the analysis host; this is a layout check, not Windows or live engine validation.

Driver creation also has observable registration side effects. The lower-level creation routine builds a construction-parameter block and calls 0x27D9FC at 0x482F873; its return becomes the new object. A global-derived outer-like value is stored at block+8 and the selected class-like value at block+0. Exact semantics of all construction fields remain unresolved.

At 0x482FFE4 the instance-name value is written to new object+0x210. After two configuration calls, the routine grows the context array at +0x208 when its count (+0x210) equals capacity (+0x214), increments the count, and appends a 16-byte pair: new driver pointer and selected definition pointer. It then calls 0xBBCF6E with the context world and new driver. Thus a rollback must account for context registration and notification, not merely release the object. No matching removal/destruction path has yet been validated.

The checker now includes 16 complete instruction windows, covering the lifetime caller, constructor, destructor, option-element cleanup and driver registration. All four supplied live table associations still match. The next unresolved items are constructor/parser failure behavior, the task-context requirement, and symmetric driver cleanup. No new live capture or build is needed for this offline update.
