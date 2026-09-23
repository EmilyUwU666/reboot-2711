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
