# Dispatch and size evidence: CL47722112, later capture

Static analysis of the captured image identifies a ProcessEvent-compatible path
at RVA 0x3729A, slot 28 (byte offset 0xE0) in Default__Object's vtable.
This is not a live invocation test, and dispatch/gameplay remains disabled.
The concrete path does the following:

- Receives object/function/parameter-buffer arguments in RCX/RDX/R8.
- Tests function flags at +0xB8 (including Native via byte +0xB9 bit 2).
- Handles call-space decisions, parameter storage and copy-in/copy-out.
- Builds an FFrame with function, object, script, locals and decoded field head.
- Calls the invocation helper at RVA 0x8D7AF44 (call site RVA 0x37626).
- That helper loads the function entry pointer from UFunction +0xE0
  at instruction RVA 0x8D7AFB3.

Do not confuse the vtable byte offset 0xE0 with the UFunction member +0xE0;
they are unrelated locations with the same numeric offset.

Additional instruction-confirmed reads:

| Field | Decode | Evidence RVA |
| --- | --- | --- |
| UObject internal index | DWORD +0x14 XOR 0x753838AB | 0xE018E9–0xE018F3 |
| UStruct property-storage size | DWORD +0x68 XOR 0x1937F47B | 0x373D5–0x373E4 |
| UFunction parameter-buffer size | WORD +0xBC XOR 0x8250 | 0x3743C–0x37449 |
| UFunction flags | DWORD +0xB8 (observed flag tests) | 0x372D9, 0x3737D, 0x37549 |
| UFunction native entry | pointer +0xE0 | 0x8D7AFB3 |

Captured cross-checks:

| Function | Storage size | Parameter-buffer size |
| --- | ---: | ---: |
| ExecuteUbergraph | 4 | 4 |
| Activate | 1 | 1 |
| GetOwner | 8 | 8 |
| ComponentHasTag | 8 | 5 |

The different storage and parameter sizes in ComponentHasTag are significant:
using one size for both would silently produce wrong bindings.

The index XOR is now supported by instructions, but the previously found
32-byte-stride object table is still not an established GUObjectArray layout.
Its 39 tail entries differ from their slot by one, so slot number must not be
used as the object's internal index. The separate indexed structure referenced
by this code needs its semantics established before using it as the registry.

Launcher integration: emilyfn-reflection-export.patch now adds the property
metadata export button, shared capture parsing and rejection tests. It emits
631 owners and 2,030 properties from this capture with zero rejected chains.
The generated C++17 header compiles. It explicitly leaves sdk_ready and
complete_reflection false. The new sizes/dispatch evidence above is recorded
for the next binding step; it is not enabled by that launcher build.
