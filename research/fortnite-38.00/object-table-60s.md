# Later-capture object inventory (2026-09-23)

The 60-second capture is complete: 2,211,334,557 bytes, 3,161 memory ranges,
128 modules and 95 threads. Game image base is 0x50000. Existing C# name
export succeeds with 153,407 plain and 100 numbered entries.

The startup log records CrashReportClient descendants shortly after debugger
detach. It does not prove a fatal crash, and the game process remained alive.
There is no exception stream in this manually captured full-memory dump.
No definite crash cause has been established.

Unlike the earlier two-second dump, this capture contains recognizable core
class objects. The observed header fields are: vtable +0x00, outer +0x08,
class pointer +0x18, encoded name index +0x20. Class is self-typed, while
Object, Actor and Function point to Class. Actor's pointer at +0x40 refers
to Object; this is a candidate superclass field, not a fully verified layout.

A table pointer at image RVA 0x16CFACD8 and count at 0x16CFACE0 expose
23,050 slots with a 32-byte stride and object pointer at slot +8.
The helper validates 23,049 unique objects; slot 22,669 does not pass the
vtable check and is reported rather than silently treated as an object.
The table's allocation/deletion semantics and relationship to GUObjectArray
are not established, so it is not yet a validated runtime registry binding.

Inventory:
- 21,214 Class
- 1,122 Package
- 352 Function
- 175 ScriptStruct
- 108 DelegateFunction
- 38 SparseDelegateFunction
- 34 Enum
- 6 remaining objects

The candidate internal index at +0x14 XOR 0x753838AB equals the table slot
for 23,010 objects. The other 39 differ by +1 and occur at the tail. This
mismatch must be explained before using the table slot as an internal index.
The candidate decoder is evidence from this snapshot, not instruction-verified.

Run `python inspect_objects.py game.dmp --output private-inventory.json` for
an offline inventory with names, class/outer pointers and candidate indices.
The optional JSON is private diagnostic output, not an SDK. Original memory,
executables and runtime name/object inventories are not published here.

Still unfinished: authoritative registry lookup, complete UClass/UStruct/
UFunction layouts, property traversal, function dispatch, server hooks and
full SDK headers. No gameplay support is enabled by this research helper.
