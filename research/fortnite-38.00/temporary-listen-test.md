# Experimental temporary listen, exact 38.00 CL47722112

Live lifecycle report 4 passed creation, one dependency initialization and named removal: zero exception, zero remaining active drivers, checked world references clear, game alive. That establishes this limited sequence, not listening or gameplay.

The next separate launcher button is **Test 38.00 temporary listen**, saving `listen-test.json`. Run it once in a fresh matching game, then close the process. It requests an ephemeral port (URL.Port=0) using the engine's configured bind interface; it does not claim loopback-only binding. There is no client-join test and it does not keep a server running.

## Evidence and sequence

A game caller at 0x47518AD–0x47518D5 passes world+0x28 as the network-notification interface, a URL reference and a zero-initialized 16-byte error string to virtual slot 93. The caller frees non-null error data through 0x8D2505C at 0x4751A18–0x4751A27. The SetWorld implementation at 0xFC3134 writes driver.World and driver+0x300 = world+0x28, with other engine side effects. This is why neither a raw world pointer nor a field-only assignment is substituted.

The new operation retains exact executable/hash, registry, empty-context, native instruction and virtual-table guards. It checks the world's secondary interface table and the expected IpNetDriver init/listen entries. After creation/identity validation it calls SetWorld, revalidates the same driver and world/notify links, constructs a temporary URL through the already-tested constructor and sets only its local Port field to zero. It invokes the fixed IpNetDriver listen implementation once, with the fifth argument pointing to an initially empty engine string. It records the boolean result, returned URL port and a bounded error text (191 UTF-16 code units maximum).

After a normal listen return, it validates error-string array bounds, frees non-null error data with the same engine free path as the observed caller, and destroys the temporary URL through the engine destructor. Normal false results also reach this cleanup. Base initialization normally initializes the shutdown dependency; the earlier validated initializer is used only if that field remains null. Named driver removal and the existing context/world-reference checks then run.

On an exception, invalid setup result or malformed output buffer, the test stops rather than freeing uncertain allocations or retrying removal. Error code, operation stage and game-relative fault details are captured. Closing the game is required after the experiment. The standard driver lifecycle and URL-only tests remain separate.

## What success means

ListenPassed requires a successful listen return, a returned port in 1–65535, released temporary buffers, successful checked driver cleanup and a live process with the diagnostic hook removed. It does not establish full gameplay, a working client connection, independent OS-level socket-closure verification, or collection of the driver's object memory. Socket teardown relies on the engine's normal removal path and remains part of the experimental validation.

Protocol v8 uses a 2048-byte mapping and adds explicit listen counters, result, port, error text and fault details. Synthetic tests cover sequence ordering and stop-on-failure at each setup/call/release stage; a real Windows callback test requires invalid targets to make zero driver/listen calls. A live game result is still required.
