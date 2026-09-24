# Observed property chains, CL47722112

The 60-second capture successfully exports 2,030 properties belonging to 631
owners: 9 Class, 164 ScriptStruct, 332 Function, 89 DelegateFunction and
37 SparseDelegateFunction. All traversed chains pass ownership checks, without
cycles or failed decoding. Most Class objects have no populated property chain;
this is incomplete reflection coverage, not proof that those classes are empty.

Observed fields:
- Owner's property head: +0x48, tagged-pointer decode below.
- FField next: +0x10, same decode.
- FField encoded name index: +0x1C (uses the verified FName decoder).
- FField owner: +0x20, clear low tag bit before comparing.
- FField class pointer: +0x08; its name index is at +0x30.
- Property element size: DWORD +0x28 XOR 0xAF687E4B.
- Property byte offset: DWORD +0x3C XOR 0xF045716B.
- Property array dimension: DWORD +0x60.

Tagged pointer: if low bit is set, clear it and XOR 0x47DCC0173F15EC38;
otherwise use the stored pointer. The element-size, byte-offset and next-pointer
rules had instruction evidence in earlier research; this capture supplies runtime
corroboration. Other fields above are observations, not a full engine ABI.

Examples: ExecuteUbergraph.EntryPoint -> IntProperty (4-byte element),
Activate.bReset -> BoolProperty (1-byte element), MaterialInput.Expression ->
ObjectProperty (8-byte element). These properties start at offset zero within
their respective owners.

`export_reflection.py` emits reflection.hpp plus JSON and a limitations report.
The header contains owner/property metadata, not C++ memory-layout structs or
callable functions. Owners use full outer-qualified names to disambiguate them.
No guessed owner sizes, property flags, bool masks or nested type bindings are
emitted. Invalid chains are rejected as a whole and recorded in the report.

Validation: compiled the actual 631-owner/2,030-property output with g++ C++17,
-Wall -Wextra -Werror. Injected a cycle and an owner mismatch into the memory
reader; both cases rejected the complete affected chain without partial output.
No original executable, dump, or generated runtime inventory is committed.

Still unfinished: authoritative object registry indexing, complete type
initialization/coverage, nested type decoding, function dispatch, server hooks,
and launcher integration of this property-level exporter. The previously built
launcher exports names only; this change is an offline research/export tool.
