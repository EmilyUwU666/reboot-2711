"""Offline PE/signature inventory; never executes the supplied game binary.

Usage: python inspect_executable.py GAME.exe SDK/Offsets.h > evidence.json
Signature matches are candidates, not verified function addresses or support.
"""
import hashlib
import json
from pathlib import Path
import re
import struct
import sys


def inspect(executable, offsets):
    data = Path(executable).read_bytes()
    if data[:2] != b'MZ':
        raise ValueError('Not a PE file')
    pe = struct.unpack_from('<I', data, 60)[0]
    if data[pe:pe + 4] != b'PE\0\0':
        raise ValueError('Invalid PE signature')
    machine, count = struct.unpack_from('<HH', data, pe + 4)
    optional_size = struct.unpack_from('<H', data, pe + 20)[0]
    optional = pe + 24
    if machine != 0x8664 or struct.unpack_from('<H', data, optional)[0] != 0x20b:
        raise ValueError('Expected AMD64 PE32+')
    sections = []
    for i in range(count):
        at = optional + optional_size + 40 * i
        name, size, rva, raw_size, raw = struct.unpack_from('<8sIIII', data, at)
        if raw + raw_size > len(data):
            raise ValueError('Section extends past file')
        sections.append(dict(name=name.rstrip(b'\0').decode('ascii'),
                             virtual_size=size, rva=rva, raw_size=raw_size, raw=raw))
    text = next(s for s in sections if s['name'] == '.text')
    code = data[text['raw']:text['raw'] + text['raw_size']]
    source = Path(offsets).read_text()
    patterns = []
    # Join adjacent C++ string literals within literal FindPattern arguments.
    for match in re.finditer(r'FindPattern\(\s*((?:"[^"]*"\s*)+)', source):
        signature = ''.join(re.findall(r'"([^"]*)"', match[1]))
        tokens = signature.split()
        if not tokens or any(not re.fullmatch(r'[0-9A-Fa-f]{2}|\?\??', t) for t in tokens):
            continue
        regex = b''.join(b'.' if '?' in t else re.escape(bytes.fromhex(t)) for t in tokens)
        hits = [text['rva'] + m.start() for m in re.finditer(regex, code, re.DOTALL)]
        patterns.append(dict(source_line=source.count('\n', 0, match.start()) + 1,
                             signature=signature, match_count=len(hits), candidate_rvas=hits))
    markers = {}
    for term in ['++Fortnite+Release-38.00-CL-47722112', 'Unreal Engine 5.7.0',
                 'JunoRootPlayspace', 'PilgrimQuickplayPlayspace', 'SparksSongCatalog']:
        markers[term] = {enc: data.find(term.encode(enc)) for enc in ('ascii', 'utf-16le')}
    return dict(schema=1, gameplay_support='unimplemented', executed=False,
                sha256=hashlib.sha256(data).hexdigest(), size=len(data),
                offsets_source_sha256=hashlib.sha256(Path(offsets).read_bytes()).hexdigest(),
                entry_rva=struct.unpack_from('<I', data, optional + 16)[0],
                sections=sections, markers=markers, literal_signature_inventory=patterns,
                limitations=['Substring presence does not establish class availability.',
                             'Static matches do not establish ABI or runtime compatibility.',
                             'Conditional, reference-based, and generated scanners are not evaluated.'])


if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    print(json.dumps(inspect(*sys.argv[1:]), indent=2))
