# Engine world-context candidate

Static wrappers at 0xA6B0BC0 and 0xC5A5984 iterate the engine pointer array at +0xFD8, using count +0xFE0 and context world field +0x2B8. The latter tail-calls creation candidate 0x482F38E, passing the original third argument in r8d and zero in r9d. A second wrapper at 0xC5A59E4 searches context +0x188 instead, so it is not interchangeable with a world-based lookup.

The launcher now checks the exact instruction bytes at 0xC5A5990 before reading this array on the unique registered FortEngine instance. It bounds the array, checks source and referenced-world internal indices, and reports context ordinal/world registry slot without raw pointers. It is a cached non-atomic observation, not an active-world selection or callable binding. Unknown capacity layout or bounds fail closed. No network driver is created, no engine call is made, and gameplay readiness remains false.
