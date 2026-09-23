"""Offline audit: python inspect_network_signatures.py 38.00.exe Reboot-27.11-Source.zip
Does not execute game code. Matches are candidates, never callable bindings.
"""
import zipfile,re,struct,json,hashlib,sys
from pathlib import Path
exe=Path(sys.argv[1]);data=exe.read_bytes()
sha=hashlib.sha256(data).hexdigest();assert sha=='f4ddac1044edd0e8cc123f586f7204de8724989b6adcf25b2e34b4855747a5c0'
pe=struct.unpack_from('<I',data,60)[0];num=struct.unpack_from('<H',data,pe+6)[0];opt=struct.unpack_from('<H',data,pe+20)[0]
sects={}
for i in range(num):
 name,size,rva,rawsize,raw=struct.unpack_from('<8sIIII',data,pe+24+opt+40*i);sects[name.rstrip(b'\0').decode()]=(rva,raw,rawsize)
rva,raw,size=sects['.text'];code=data[raw:raw+size]
z=zipfile.ZipFile(sys.argv[2]);src=z.read('Reboot-27.11-Source/Erbium/Erbium/Private/Finders.cpp').decode('utf-8-sig')
result={'sha256':sha,'callable':False,'patterns':[],'strings':{}}
for name in ['GetWorldContext','CreateNetDriverWorldContext','InitListen','SetWorld']:
 start=src.index('uint64_t Find'+name+'()');end=src.find('\nuint64_t ',start+10);body=src[start:end]
 for pat in re.findall(r'FindPattern\("([^"]+)"',body):
  regex=b''.join(b'.' if '?' in t else re.escape(bytes.fromhex(t)) for t in pat.split())
  hits=[rva+m.start() for m in re.finditer(regex,code,re.S)]
  result['patterns'].append(dict(finder=name,pattern=pat,hits=[hex(h) for h in hits]))
for s in ['%s IpNetDriver listening on port %i','CreateNamedNetDriver','Failed to create net driver','WorldContext','InitListen','SetWorld']:
 b=s.encode('utf-16le');result['strings'][s]=[hex(m.start()) for m in re.finditer(re.escape(b),data)][:20]
print(json.dumps(result,indent=2))
