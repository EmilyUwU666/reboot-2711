#!/usr/bin/env python3
"""Inspect the exact supplied 38.00 PE offline. Never loads or calls the image.
Usage: python inspect_network_contracts.py IMAGE [--live-report dispatch-test.json]
Requires capstone. Output is evidence, not a callable SDK or startup approval.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path
import capstone

EXPECTED = "f4ddac1044edd0e8cc123f586f7204de8724989b6adcf25b2e34b4855747a5c0"
RANGES = {
    "DeferredRemovalConsumer": (0x335924, 0x335AC6),
    "NamedRemovalWorldWrapper": (0xA64AFBC, 0xA64B00F),
    "NamedRemovalContext": (0x1F551F0, 0x1F554BA),
    "ActiveDriverRemoveSwap": (0xAA162EC, 0xAA16362),
    "DeferredRemovalRequest": (0xC3D7254, 0xC3D7290),
    "DeferredRemovalFlagWrite": (0x464D5CD, 0x464D604),
    "WorldDriverReferenceCleanup": (0xC56FD12, 0xC56FD7C),
    "WorldNetworkShutdown": (0x482EF38, 0x482F26A),
    "UrlDefaultConstruction": (0xB2FC82, 0xB2FF2B),
    "UrlParseConstructionPrefix": (0x47CEE60, 0x47CF009),
    "UrlDestruction": (0x1B609FA, 0x1B60A75),
    "UrlOptionElementsDestruction": (0x8D2FFEF, 0x8D3001C),
    "UrlLifetimeCaller": (0xC5A644D, 0xC5A6573),
    "DriverObjectConstruction": (0x482F81F, 0x482F8C0),
    "DriverContextRegistration": (0x482FFDA, 0x4830065),
    "IpListenForwarding": (0x49354B8, 0x4935504),
    "IpListenSuccess": (0x4935504, 0x493552A),
    "IpListenErrorString": (0x493561A, 0x493562E),
    "NamedCreationArguments": (0x1FAFE74, 0x1FAFEAB),
    "NamedCreationReturn": (0x1FAFF9E, 0x1FAFFC4),
    "DefinitionSelection": (0x482F3BB, 0x482F46F),
    "NamedDriverLookup": (0x482F26A, 0x482F2D9),
    "WorldCreationWrapper": (0xA6B0BC0, 0xA6B0C24),
    "UrlOptions": (0x155CC07, 0x155CC7D),
}
TABLES = {
    "/Script/Engine.NetDriver": (0x11CA8470, [0xC306F9A, 0x4655228, 0xFC3134]),
    "/Script/OnlineSubsystemUtils.IpNetDriver": (0x11E085C0, [0xC306F9A, 0x49354B8, 0xFC3134]),
    "/Script/Engine.DemoNetDriver": (0x11B9D340, [0xC306F9A, 0xC30583C, 0xFC2ECE]),
    "/Script/SocketSubsystemEOS.NetDriverEOSBase": (0x1220CC80, [0xC306F9A, 0x500F0CA, 0xFC3134]),
}

def inspect(path, live_report=None):
    data = Path(path).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED:
        raise ValueError("Unsupported image SHA-256; no offsets were inspected.")
    pe = struct.unpack_from("<I", data, 0x3c)[0]
    count = struct.unpack_from("<H", data, pe + 6)[0]
    optsize = struct.unpack_from("<H", data, pe + 20)[0]
    imagebase = struct.unpack_from("<Q", data, pe + 24 + 24)[0]
    sections = []
    for i in range(count):
        at = pe + 24 + optsize + i * 40
        _, rva, size, raw = struct.unpack_from("<IIII", data, at + 8)
        sections.append((rva, size, raw))
    def read(rva, size):
        for start, length, raw in sections:
            if start <= rva and rva + size <= start + length:
                return data[raw + rva - start:raw + rva - start + size]
        raise ValueError(f"RVA 0x{rva:X} is not fully file-backed")
    cs = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)
    evidence = {}
    for name, (start, end) in RANGES.items():
        code = read(start, end - start)
        ins = list(cs.disasm(code, start))
        if sum(i.size for i in ins) != len(code):
            raise ValueError(f"Incomplete disassembly: {name}")
        evidence[name] = {"StartRva": hex(start), "EndRvaExclusive": hex(end),
            "Sha256": hashlib.sha256(code).hexdigest(),
            "Instructions": [f"0x{i.address:X}: {i.mnemonic} {i.op_str}".rstrip() for i in ins]}
    cleanup_tables = []
    cleanup_expected = {
        0x11CA8470: (0x4641FFA, 0x1C44944),
        0x11E085C0: (0x4641FFA, 0x4937BF0),
        0x11B9D340: (0x4641FFA, 0x1C44944),
        0x1220CC80: (0x500F4BE, 0x4937BF0),
    }
    for name, (table, _) in TABLES.items():
        targets = tuple(struct.unpack("<Q", read(table + slot * 8, 8))[0] - imagebase for slot in (100, 101))
        if targets != cleanup_expected[table]:
            raise ValueError(f"Unexpected file cleanup entries: {name}")
        cleanup_tables.append({"Class": name, "TableRva": hex(table),
            "Slot100": hex(targets[0]), "Slot101": hex(targets[1]),
            "LiveEntryBytesVerified": False})
    tables = []
    live = None
    if live_report:
        live = json.loads(Path(live_report).read_text())
        if live.get("ExecutableSha256") != digest:
            raise ValueError("Live report image does not match")
    for name, (table, expected) in TABLES.items():
        entries = [struct.unpack("<Q", read(table + slot * 8, 8))[0] - imagebase for slot in (50, 93, 130)]
        if entries != expected:
            raise ValueError(f"Unexpected file table entries: {name}")
        live_match = None
        if live:
            drivers = live.get("Evidence", {}).get("NetDriverBindings", {}).get("Drivers", [])
            matches = [d for d in drivers if d.get("ClassName") == name]
            live_match = len(matches) == 1
            if live_match:
                d = matches[0]
                methods = d.get("Methods", [])
                live_match = (d.get("Failure") is None and d.get("ClassMatches") == 1
                    and d.get("DefaultMatches") == 1 and d.get("VtableRva") == f"0x{table:X}"
                    and len(methods) == 3 and all(m.get("Slot") == slot and m.get("EntryRva") == f"0x{entry:X}"
                        for m, slot, entry in zip(methods, (50, 93, 130), entries)))
        tables.append({"Class": name, "TableRva": hex(table),
            "Slots": dict(zip((50, 93, 130), map(hex, entries))),
            "SuppliedLiveReportMatchesFileTable": live_match})
    return {"ImageSha256": digest, "NetworkingCallsAttempted": False,
        "CallableBindingsVerified": False, "InstructionEvidence": evidence, "Tables": tables, "CleanupTables": cleanup_tables,
        "Limitations": "Report correlation trusts supplied JSON. File table matches do not validate live method bytes, full parameter layouts, construction, engine task tags, or side effects."}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("--live-report")
    args = parser.parse_args()
    print(json.dumps(inspect(args.image, args.live_report), indent=2))
