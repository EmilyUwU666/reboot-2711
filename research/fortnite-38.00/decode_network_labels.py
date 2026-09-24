"""Offline candidate discovery from an observed encoded-string copy/decode pattern.
Usage: python decode_network_labels.py 38.00.exe
Labels and runtime-function ranges are static evidence, not callable bindings.
"""
from pathlib import Path
import re,struct,bisect,json,hashlib,sys
b=Path(sys.argv[1]).read_bytes();assert hashlib.sha256(b).hexdigest()=='f4ddac1044edd0e8cc123f586f7204de8724989b6adcf25b2e34b4855747a5c0', 'Exact 38.00 image required'
pd=b[387907584:398110720];fs=sorted(struct.unpack_from('<III',pd,i) for i in range(0,len(pd)-11,12));ss=[f[0] for f in fs]
pat=rb'\x48\x8d\x15(....).{0,12}?\x41\xb8(....)\xe8....\xb0(.)'
out=[]
for m in re.finditer(pat,b[:0x1121e000],re.S):
 a=m.start();p=a+7+struct.unpack('<i',m[1])[0];n=struct.unpack('<I',m[2])[0];key=m[3][0]
 if not(4<=n<=2048 and n%2==0 and 0<=p<=len(b)-n):continue
 decoded=bytearray()
 for v in b[p:p+n]:key=(key*97+68)&255;decoded.append(v^key)
 try:s=decoded.decode('utf-16le').rstrip('\0')
 except UnicodeDecodeError:continue
 if not any(t in s.lower() for t in ['createnamednetdriver','ipnetdriver listening','failed to init net driver listenurl','init as ipnetdriver listen server','netdriver::shutdown','world netdriver shutdown']):continue
 f=fs[bisect.bisect_right(ss,a)-1];row=dict(reference=hex(a),function=[hex(f[0]),hex(f[1])],encoded_data=hex(p),length=n,seed=m[3][0],text=s);out.append(row)
print(json.dumps(out,indent=2))
