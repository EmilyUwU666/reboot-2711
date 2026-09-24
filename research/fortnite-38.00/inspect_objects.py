#!/usr/bin/env python3
"""Offline object inventory for CL47722112; does not call game code or generate an SDK.

Usage: python inspect_objects.py game.dmp [--output private-inventory.json]
The optional output contains captured runtime names. Keep it private.
"""
import argparse
import bisect
import collections
import json
import mmap
import struct

class Capture:
    def __init__(self, path):
        self.file = open(path, 'rb')
        self.memory = mmap.mmap(self.file.fileno(), 0, access=mmap.ACCESS_READ)
        self.ranges = []
        if self.memory[:4] != b'MDMP':
            raise ValueError('Not a minidump')
        count, directory = self.unpack('II', 8)
        if not 0 < count <= 128:
            raise ValueError('Invalid stream count')
        streams = {}
        for i in range(count):
            kind, size, offset = self.unpack('III', directory + 12*i)
            if offset + size > len(self.memory):
                raise ValueError('Truncated stream')
            if kind:
                if kind in streams: raise ValueError('Duplicate stream')
                streams[kind] = (size, offset)
        size, r = streams[9]
        count, data = self.unpack('QQ', r)
        if count > 1000000 or size < 16 + count*16:
            raise ValueError('Invalid full-memory directory')
        for i in range(count):
            a, n = self.unpack('QQ', r + 16 + i*16)
            if data+n > len(self.memory): raise ValueError('Incomplete memory payload')
            if n: self.ranges.append((a, a+n, data))
            data += n
        self.ranges.sort()
        if any(a[1] > b[0] for a,b in zip(self.ranges,self.ranges[1:])):
            raise ValueError('Overlapping memory ranges')
        self.starts = [a for a,e,o in self.ranges]
        size,r = streams[4]
        count = self.unpack('I',r)[0]
        if size < 4+count*108: raise ValueError('Invalid module list')
        matches=[]
        for i in range(count):
            a,n,_,_,nr=self.unpack('QIIII',r+4+i*108)
            length=self.unpack('I',nr)[0]
            if length>65536 or length%2: raise ValueError('Invalid module name')
            name=self.at(nr+4,length).decode('utf-16le').replace('\\','/').split('/')[-1]
            if name.lower()=='fortniteclient-win64-shipping.exe': matches.append((a,n))
        if len(matches)!=1 or matches[0][1]!=0x18777000:
            raise ValueError('Unsupported game image')
        self.base=matches[0][0]
        # Compatibility checks, not whole-image authentication.
        if self.read(self.base+0x28dae,27).hex()!='8b0185c07413ffc8352b62016fffc0bfd59dfe900f45f8eb0231ff':
            raise ValueError('Unsupported FName index instructions')
        if self.read(self.base+0x16c1c5a8,1)!=b'\x01': raise ValueError('Name pool not ready')
        self.pool=self.base+0x16c1c5c0
        self.block=self.dword(self.pool+8)
        self.cursor=self.dword(self.pool+12)
        if self.block>=2048 or self.cursor>131072: raise ValueError('Invalid name pool')
        self.cache={}
    def at(self,o,n):
        if o<0 or n<0 or o+n>len(self.memory): raise ValueError('Truncated file')
        return self.memory[o:o+n]
    def unpack(self,fmt,o):
        return struct.unpack('<'+fmt,self.at(o,struct.calcsize('<'+fmt)))
    def read(self,a,n):
        data=bytearray()
        while n:
            i=bisect.bisect_right(self.starts,a)-1
            if i<0: raise ValueError('Unmapped memory')
            start,end,offset=self.ranges[i]
            if not start<=a<end: raise ValueError('Unmapped memory')
            take=min(n,end-a);data.extend(self.at(offset+a-start,take));a+=take;n-=take
        return bytes(data)
    def qword(self,a):return struct.unpack('<Q',self.read(a,8))[0]
    def dword(self,a):return struct.unpack('<I',self.read(a,4))[0]
    @staticmethod
    def index(stored):
        return (((((stored-1)^0x6f01622b)+1)&0xffffffff) or 0x90fe9dd5) if stored else 0
    def name(self,stored,depth=0):
        index=self.index(stored)
        if index in self.cache:return self.cache[index]
        if depth>1:raise ValueError('Nested/cyclic name reference')
        block,offset=index>>16,(index&65535)*2
        limit=self.cursor if block==self.block else 131072
        if block>self.block or offset+2>limit:raise ValueError('Invalid name index')
        a=self.qword(self.pool+16+block*8)+offset
        header=struct.unpack('<H',self.read(a,2))[0];length=(header>>6)^0x26f
        if length==0:
            if offset+10>limit:raise ValueError('Truncated numbered entry')
            stored_number=self.dword(a+2);v=(stored_number-1)&0xffffffff
            number=(v if v==0x0685c294 else v^0xf97a3d6b) if stored_number else 0xffffffff
            if number>=0x80000000:number-=0x100000000
            text=self.name(self.dword(a+6),depth+1)+'_'+str(number)
        else:
            size=length*(1+(header&1))
            if offset+2+size>limit:raise ValueError('Truncated name')
            state=length;plain=bytearray()
            for value in self.read(a+2,size):
                state=(state*0xffffde61+0xfe93e844)&0xffffffff
                plain.append(value^((state+0x4a)&255))
            text=plain.decode('utf-16le') if header&1 else ''.join(chr(v if v<128 else 0xff00+v) for v in plain)
        self.cache[index]=text
        return text
    def inventory(self):
        table=self.qword(self.base+0x16cfacd8);count=self.dword(self.base+0x16cface0)
        if not table or not 1<=count<=1000000:raise ValueError('Object table unavailable')
        objects=[];invalid=[];seen=set()
        for slot in range(count):
            try:
                address=self.qword(table+slot*32+8)
                vtable=self.qword(address)
                if not self.base<=vtable<self.base+0x18777000:raise ValueError('Invalid vtable')
                if not self.base<=self.qword(vtable)<self.base+0x11000000:raise ValueError('Invalid virtual function')
                klass=self.qword(address+0x18)
                name=self.name(self.dword(address+0x20))
                class_name=self.name(self.dword(klass+0x20))
                if address in seen:raise ValueError('Duplicate object')
                seen.add(address)
                objects.append(dict(slot=slot,address=hex(address),name=name,class_name=class_name,
                    class_address=hex(klass),outer_address=hex(self.qword(address+8)),
                    candidate_index=self.dword(address+0x14)^0x753838ab))
            except (ValueError,UnicodeError) as error:
                invalid.append(dict(slot=slot,reason=str(error)))
        by_name={o['name']:o for o in objects if o['class_name']=='Class'}
        for required in ['Object','Class','Actor','Function']:
            if required not in by_name:raise ValueError('Core class missing: '+required)
        if by_name['Class']['address']!=by_name['Class']['class_address']:
            raise ValueError('Class does not refer to itself')
        return dict(profile='38.00 CL47722112 object-table research',sdk_ready=False,
            registry_layout_verified=False,function_dispatch_verified=False,
            slots=count,readable_objects=len(objects),invalid_slots=invalid,
            candidate_index_matches=sum(o['candidate_index']==o['slot'] for o in objects),
            class_counts=dict(collections.Counter(o['class_name'] for o in objects)),objects=objects)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('dump');parser.add_argument('--output');args=parser.parse_args()
    capture=Capture(args.dump);result=capture.inventory()
    if args.output:
        with open(args.output,'w',encoding='utf-8') as out:json.dump(result,out,indent=2)
    print(json.dumps({k:v for k,v in result.items() if k!='objects'},indent=2))
