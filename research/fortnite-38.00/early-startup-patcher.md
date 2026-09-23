# CL47722112 early startup patcher test

The 2026-09-23 20:23 UTC dispatch report successfully delivered a GameThread
callback, removed its hook and left the game alive. All 23,051 registry entries
matched their internal indices. The required Default__ActorComponent was absent,
so no Unreal function was invoked. Twelve main-image callback return RVAs were
captured, including 0x3FB16B, 0x3FAB38, 0x201A9E5 and 0x201A723.

Those frames locate a specific early startup loop. Function 0x201A730 calls the
active screen's virtual IsDone method at slot +0x40. While it returns false,
0x3FAACA/0x3FB088 ticks that screen and pumps Windows messages. The observed
0x3FB16B return address follows the message-pump call. Callback delivery therefore
does not establish that engine startup or game objects are ready.

The previously supplied later memory capture has the same startup path. Global
RVA 0x16E1B900 points to a screen with vtable RVA 0x1543A2E0, Tick 0x8B84524,
IsDone 0x70F7664 and type method 0x1A38C0. IsDone returns byte +0x75. Analysis
of Tick and the completion callbacks establishes these separate observations:

| Object offset | Observed field | Later capture |
| --- | --- | --- |
| +0x63 | Minimum display interval elapsed | true |
| +0x74 | Patching completed | false |
| +0x75 | Screen finished | false |
| +0x184 | Combined progress | 0 |
| +0x188 | Download progress | 0 |
| +0x18C | Install progress | 0 |
| +0x1F8 | Raw patch state; enum meaning unverified | 0 |

Decoded diagnostic strings in these routines identify FFortniteEarlyPreLoadScreen
and its wait for patch progress. This locates the wait, but does not establish
which bundle, request, dependency or external service prevented completion.

The supplied image contains the UTF-16 SkipPatchCheck parameter at RVA 0x160689A8.
FPatchCheck's routine 0x487FCF2 parses it through FParse::Param at call site
0x487FD57; 0xA5A10DA also parses it into that routine's configuration object.
This is evidence that the switch is implemented, not proof that it controls
every prerequisite of the observed early screen. The new diagnostic launch adds
the switch as a candidate startup test. It does not write completion flags,
construct substitute objects, change any DLL function-call gate or enable normal
38.00 gameplay. The normal Play path is unchanged.

The read-only evidence records only whether the exact argument token was seen.
FCommandLine's verified accessor points to initialized byte RVA 0x16BE4514 and
UTF-16 buffer 0x16BE4520. Reading is bounded to 16 KiB; missing, uninitialized or
unterminated data yields null rather than false. Neither raw command lines nor
credential-bearing strings are written to reports. Command-line unavailability
does not discard otherwise valid patcher fields.

Exact instruction anchors and three virtual entries gate the field reads. An
absent screen is reported as inactive with unknown completion, never as success.
Unexpected booleans, non-finite progress, mismatched layouts and unreadable state
are rejected. Live reads remain non-atomic, and progress may change between reads.
No screen observation establishes lobby access or gameplay readiness.

The new Launch 38.00 diagnostic action uses the same exact executable hash and
complete-installation checks as startup capture, but omits debugging and memory
dumps. It records process identity and an exit code if observed after 1.5 seconds,
then selects the running process for the existing small JSON tests. It leaves
that diagnostic process running for the user to inspect and close manually.

Validation: the offline reader matched all instruction anchors and the table
above in the supplied later capture, with SkipPatchCheckTokenObserved=false and
no rejected patcher fields. Synthetic checks exercise token privacy/boundaries,
unavailable command data, inactive and different screens, malformed fields and
instruction mismatches. Windows fixtures must also reject a different executable
through the new launch entry point. Only a subsequent user live test can confirm
whether the switch advances this startup state.

Materialize emilyfn-patcher-startup.patch after emilyfn-startup-stack.patch.
