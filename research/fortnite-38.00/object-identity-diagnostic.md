# Post-name-decoding core identity diagnostic

The 2026-09-23 21:45 UTC live report no longer fails name decoding. Instead all
three fresh verification attempts report Required core class missing: Object.
The early patcher remains inactive and SkipPatchCheck is observed. No callback
or Unreal function was attempted. BindingReadAttempts.Decoded describes completion
of the full inspection, so false here does not mean name decoding failed again.

The core-class check occurs after registry enumeration and object-header reads.
Previously individual header failures were counted but their reasons discarded;
the exception then prevented partial counts from reaching the JSON. The report
therefore cannot distinguish rejected registry entries, rejected object headers,
unavailable name indices or readable objects whose kinds do not match Class.
It does not prove that Fortnite lacks its Object class.

Both live and dispatch JSON reports now preserve ObjectIdentity before core-class
requirements are enforced. It records decoded-name count, registry slots,
accepted/empty/rejected registry entries, readable/rejected object headers,
aggregated header rejection reasons, the known core names' pool indices and
matching core-class counts. At most twelve registry rejection samples, twelve
rejected-header samples and twelve accepted-header samples are included.

Header samples contain slot and decoded name indices, whitelisted core-name
labels, and in-image relative vtable/function offsets. Outside-image pointers
and arbitrary runtime name strings are not exported. Registry mismatches include
the observed internal index alongside the expected slot. Optional sample reads
are bounded and use the existing read cache/deadline. Evidence is cleared before
each retry so a failed later attempt cannot masquerade as earlier current data.

The native dispatch gate, core lookup, property checks, pointer decoding and
virtual-function checks are unchanged. In particular no missing-class check is
disabled and no layout fix is guessed from the generic failure message.

Fixture tests distinguish an invalid Object vtable from an Object registry-index
mismatch, verify partial evidence survives each failure, omit outside-image
pointers, and check successful core identities after restoration. The previous
full capture still passes its existing decoding/reflection checks. A new small
live report is needed to identify which condition affects the initialized game.

Materialize emilyfn-object-identity.patch after emilyfn-short-name-tails.patch.
