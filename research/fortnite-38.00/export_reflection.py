#!/usr/bin/env python3
"""Export observed CL47722112 reflection metadata, not callable SDK bindings.
Usage: python export_reflection.py game.dmp output-directory
Keep generated runtime metadata private. No game code is executed.
"""
import argparse
import collections
import hashlib
import json
from pathlib import Path
from inspect_objects import Capture

KINDS={'Class','ScriptStruct','Function','DelegateFunction','SparseDelegateFunction'}

def decode_link(value):
    return ((value & ~1) ^ 0x47dcc0173f15ec38) if value & 1 else value

def reflected_properties(capture,inventory):
    rows=[];errors=[];owners={};qualified_cache={}
    def qualified(address):
        if address in qualified_cache:return qualified_cache[address]
        names=[];seen=set();a=address
        while a:
            if a in seen or len(seen)>=64:raise ValueError('Cyclic/excessive outer chain')
            seen.add(a);names.append(capture.name(capture.dword(a+0x20)));a=capture.qword(a+8)
        value='.'.join(reversed(names));qualified_cache[address]=value;return value
    for obj in inventory['objects']:
        if obj['class_name'] not in KINDS or obj['name'].startswith('Default__'):continue
        a=int(obj['address'],16);chain=[]
        try:
            owner=qualified(a);p=decode_link(capture.qword(a+0x48));seen=set()
            while p:
                if p in seen or len(seen)>=4096:raise ValueError('Cyclic/excessive field chain')
                seen.add(p)
                if capture.qword(p+0x20)&~1 != a:raise ValueError('Property owner mismatch')
                name=capture.name(capture.dword(p+0x1c))
                field_class=capture.qword(p+8)
                if not capture.base<=field_class<capture.base+0x18777000:raise ValueError('Field class outside image')
                typ=capture.name(capture.dword(field_class+0x30))
                if not typ.endswith('Property'):raise ValueError('Unexpected field type')
                offset=capture.dword(p+0x3c)^0xf045716b
                size=capture.dword(p+0x28)^0xaf687e4b
                dimension=capture.dword(p+0x60)
                if offset>0x1000000 or not 0<size<=0x1000000 or not 0<dimension<1000000:
                    raise ValueError('Implausible property extent')
                if size*dimension>0x1000000:raise ValueError('Oversized property extent')
                chain.append(dict(owner=owner,name=name,type=typ,offset=offset,element_size=size,array_dim=dimension))
                p=decode_link(capture.qword(p+0x10))
            if chain:
                owners[owner]=obj['class_name'];rows.extend(chain)
        except (ValueError,UnicodeError) as error:
            # Do not export a partially validated chain.
            errors.append(dict(owner=obj['name'],reason=str(error)))
    return owners,rows,errors

def cpp_string(value):
    return '"'+''.join('\\'+format(b,'03o') for b in value.encode('utf-8'))+'"'

def export(capture,folder):
    inventory=capture.inventory();owners,rows,errors=reflected_properties(capture,inventory)
    folder=Path(folder)
    # Never overwrite a prior export or unrelated files.
    folder.mkdir(parents=True,exist_ok=False)
    order=sorted(owners);ids={name:i for i,name in enumerate(order)}
    rows.sort(key=lambda r:(ids[r['owner']],r['offset'],r['name']))
    report=dict(profile='38.00 CL47722112',source_dump_bytes=len(capture.memory),
        source_sha256=hashlib.sha256(capture.memory).hexdigest(),
        sdk_ready=False,complete_reflection=False,function_dispatch_verified=False,
        reflected_owners=len(owners),properties=len(rows),
        owner_kinds=dict(collections.Counter(owners.values())),
        inventory_readable_objects=inventory['readable_objects'],
        inventory_invalid_slots=inventory['invalid_slots'],chain_errors=errors,
        limitations=['Most captured classes have no populated property chain.',
                     'Owner structure sizes, property flags, nested type references and bool masks are not exported.',
                     'No ProcessEvent bindings, callable function wrappers or server hooks.'])
    (folder/'reflection.json').write_text(json.dumps(dict(report=report,owners=owners,properties=rows),indent=2),encoding='utf-8')
    with (folder/'reflection.hpp').open('w',encoding='utf-8') as f:
        f.write('#pragma once\n#include <array>\n#include <cstdint>\nnamespace emilyfn_capture38 {\n')
        f.write('// Observed metadata only; this is NOT a complete or callable gameplay SDK.\n')
        f.write('inline constexpr bool sdk_ready = false;\ninline constexpr bool complete_reflection = false;\n')
        f.write('struct Owner { const char* name; const char* kind; };\n')
        f.write('struct Property { std::uint32_t owner; const char* name; const char* type; std::uint32_t offset, element_size, array_dim; };\n')
        f.write('inline constexpr std::array<Owner, '+str(len(order))+'> owners = {{\n')
        for name in order:f.write('{'+cpp_string(name)+','+cpp_string(owners[name])+'},\n')
        f.write('}};\ninline constexpr std::array<Property, '+str(len(rows))+'> properties = {{\n')
        for r in rows:
            f.write('{'+str(ids[r['owner']])+'u,'+cpp_string(r['name'])+','+cpp_string(r['type'])+','+','.join(str(r[k])+'u' for k in ['offset','element_size','array_dim'])+'},\n')
        f.write('}};\n}\n')
    (folder/'README.txt').write_text('Observed 38.00 reflection metadata only. This is not a full SDK and does not enable gameplay.\nSee reflection.json for coverage and rejected chains. No inferred missing fields or callable wrappers are included.\nNames are from captured runtime memory; keep these generated files private.\n',encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dump');parser.add_argument('output');args=parser.parse_args()
    result=export(Capture(args.dump),args.output)
    print(json.dumps(result,indent=2))
