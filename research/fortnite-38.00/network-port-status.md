# 38.00 network startup investigation

Exact image SHA-256: `f4ddac1044edd0e8cc123f586f7204de8724989b6adcf25b2e34b4855747a5c0`. Recovered the original supplied 38.00 ZIP and verified the extracted executable against the successful live-test hash. No executable or user dump is committed.

## Legacy signature audit

The available Reboot-27.11-Source.zip contains 23 pattern alternatives across GetWorldContext (7), CreateNetDriverWorldContext (9), InitListen (4), and SetWorld (3). All have zero matches in the exact 38.00 text section. This checks literal patterns only, not every fallback finder path. `inspect_network_signatures.py` reproduces this audit and outputs the accompanying JSON.

## Static candidates, not approved calls

- The UTF-16 string UNetDriver::InitListen at image/file offset 0x15FEA5BC has a RIP-relative LEA reference at RVA 0x4655291 in the runtime-function interval 0x4655228–0x46552CA. The routine calls another function and returns 1; its visible body does not demonstrate socket setup. Do not substitute it for the legacy listen wrapper.
- A pointer to 0x4655228 occurs at 0x11CA8758. A contiguous code-pointer run starts at 0x11CA8470, making it candidate slot 93. The run has not yet been linked to a live NetDriver class-default object's vtable; these slot numbers remain provisional.
- Candidate slot 50 points to 0xC306F9A, whose initial instructions return [rcx+0x1B0].
- Candidate slot 130 points to 0xFC3134 (runtime interval ends at 0xFC32A4). It saves the second argument, reads the existing [this+0x1B0], performs cleanup, and assigns the second argument to that field at 0xFC31A9. It also updates related state and invokes other routines. The live reflection report independently identified NetDriver.World at 0x1B0. This supports a SetWorld candidate, not a validated callable binding.

## Remaining validation

Resolve the live NetDriver/IpNetDriver class-default vtables, correlate the provisional slots and concrete overrides, and verify instruction bytes after relocation. Derive the actual listen wrapper and its parameter contract. World-context lookup and driver creation remain unresolved. Do not enable startup based only on a string, legacy signature, or a candidate slot. The existing guarded GetOwner test does not validate these state-changing calls or Unreal task tags.

No gameplay gate, native hook, network-encryption setting, or server startup behavior is changed by this investigation. No new launcher build is required for these research-only files.

## Concrete listen override and creation candidates

Further static analysis found five candidate tables sharing both the getter at slot 50 (0xC306F9A) and setter at slot 130 (0xFC3134):

| Provisional table RVA | Provisional slot 93 |
| --- | --- |
| 0x11CA8470 | 0x4655228 |
| 0x11E085C0 | 0x49354B8 |
| 0x11E1B630 | 0x49354B8 |
| 0x1220CC80 | 0x500F0CA |
| 0x12496770 | 0x49354B8 |

The routine at 0x49354B8–0x49356A4 invokes virtual slot 91 with a false second argument and forwarded parameters. On success it calls slot 95, accesses an object at this+0x7C8, invokes that object's slot 7, and stores the returned integer at the third argument+0x20. Its decoded logging labels are `%s IpNetDriver listening on port %i` and `Failed to init net driver ListenURL: %s: %s`. These facts support an IP-driver listen candidate and a possible URL port field; they do not establish the complete FURL layout or approve a call.

The override at 0x500F0CA–0x500F4BE directly calls 0x49354B8 and decodes `Init as IPNetDriver listen server. LocalURL = (%s)`. The concrete class owning each table remains unverified.

The encoded labels use a byte recurrence k=(97*k+68) mod 256 followed by XOR, with an immediate seed and bounded byte count. `decode_network_labels.py` reproduces selected networking labels from this exact SHA-256-checked image. Its instruction-pattern matches remain candidate evidence, not a general decoder or function signature.

The routine at 0x1FAFE5E–0x1FB00AD contains two CreateNamedNetDriver labels, checks a collection at its second argument+0x208, and directly calls 0x482F38E. It passes its original fourth argument in r8d and original third argument in r9d, and tests the returned pointer. The callee (runtime interval 0x482F38E–0x4830253) reads engine-side array fields at rcx+0xF50/+0xF58 and decodes name indices using the already observed XOR constant 0x6F01622B. It includes a driver-definition failure label. This is a stronger driver-creation candidate, but names, definition-vs-driver-name argument order, object ownership and the calling contract still require verification.

No live network function has been invoked. World-context lookup remains unresolved. Next, correlate these tables with live NetDriver class defaults and derive the world-context and construction contracts before adding a state-changing test. This investigation does not require repeating the unchanged GetOwner test.

## Update: live table correlation and argument contracts

Report 15 resolves the live class-default table associations for NetDriver, IpNetDriver and NetDriverEOSBase, and supplies DemoNetDriver's distinct table. See `network-contracts.md` and `network-contract-evidence.json` for the superseding observations and exact argument-forwarding evidence. Earlier unresolved-table statements above describe the historical static investigation. Callable bindings and hosting remain unverified.
