#!/usr/bin/env python3
"""Independent pin/net graph comparison: exported KiCad XML versus SPICE.
Passive two-terminal parts are compared without polarity; electrolytics, diodes,
BJTs, MOSFETs, trimmer and external connector pin assignments are directional.
"""
from pathlib import Path
import xml.etree.ElementTree as E
import json,re,hashlib
P=Path(__file__).resolve().parents[1]
r=E.parse(P/'work/stereo.xml').getroot()
actual={(n.attrib['ref'],n.attrib['pin']):net.attrib['name'] for net in r.findall('nets/net') for n in net}
components={c.attrib['ref']:c for c in r.findall('components/comp')}
checks=[]
for ch in [1,2]:
 off=ch*100; side='LEFT'if ch==1 else'RIGHT'; mapping={}; reverse={}
 def bind(net,ref,pin):
    key=(ref,str(pin));a=actual[key]
    assert mapping.get(net,a)==a, f'{side}: {ref}.{pin} {a} contradicts {net}={mapping.get(net)}'
    assert reverse.get(a,net)==net,f'{side}: {net} shorts to {reverse.get(a)} on {a}'
    mapping[net]=a;reverse[a]=net;checks.append(f'{ref}.{pin}={net}')
 bind('IN','J'+str(ch+2),1);bind('SPK','J'+str(ch+4),1)
 for pin,node in [(1,'VP'),(2,'0'),(3,'VN')]:bind(node,'J'+str(ch),pin)
 passive=[]
 for line in (P/'simulation/channel.cir').read_text().splitlines():
    if not line or line[0] in '*.' :continue
    # VTHN/VTHP: zero-volt simulation-only gate series sources for imposed threshold shifts; GNI/GPI = GN/GP.
    if line.startswith('VTH'):continue
    t=line.replace('GNI','GN').replace('GPI','GP').split();ref=t[0];kind=ref[0]
    if ref.startswith('XQ'):
        rr='Q'+str(off+int(ref[2:]));pairs={2:t[1],1:t[2],3:t[3]}
    elif ref.startswith('DZ'):
        rr='D'+str(off+8+int(ref[2:]));pairs={1:t[2],2:t[1]}
    elif ref=='RV1':
        rr='RV'+str(off+1);pairs={1:t[1],2:t[2],3:t[2]}
    elif kind=='Q':
        rr='Q'+str(off+int(ref[1:]));bd=t[4].startswith('BD');pairs=({2:t[1],3:t[2],1:t[3]}if bd else{1:t[1],2:t[2],3:t[3]})
        assert components[rr].findtext('value')==('BD'+t[4][2:5] if bd else t[4][:5]),(rr,t[4])
    elif kind=='D':rr='D'+str(off+int(ref[1:]));pairs={1:t[2],2:t[1]}
    elif kind in ['R','C']:
        rr=kind+str(off+int(ref[1:]))
        if kind=='C'and ref in ['C5','C6']:pairs={1:t[1],2:t[2]}
        else:passive.append((rr,t[1:3]));continue
    else:raise AssertionError('unhandled '+line)
    for pin,net in pairs.items():bind(net,rr,pin)
 passive += [('R'+str(off+26),['OUT','SPK']),('L'+str(off+1),['OUT','SPK'])]
 while passive:
    progress=False
    for rr,nets in passive[:]:
        a=[actual[(rr,str(i))]for i in [1,2]]
        known=[i for i,n in enumerate(nets)if n in mapping]
        if not known:continue
        k=known[0];an=mapping[nets[k]];assert an in a,f'{side}: {rr} missing {nets[k]}; has {a}'
        idx=a.index(an);bind(nets[1-k],rr,2 if idx==0 else 1)
        if len(known)==2:assert set(a)=={mapping[n]for n in nets},rr
        checks.append(rr+' passive '+','.join(nets));passive.remove((rr,nets));progress=True
    assert progress,'Unmapped passives '+str(passive)
 for n,net in [(1,'SN'),(2,'OUT'),(3,'SP'),(4,'VP'),(5,'VN')]:bind(net,'TP'+str(off+n),1)
 bind('BP','J'+str(off+1),1);bind('BN','J'+str(off+1),2)
 assert len(mapping)==len(set(mapping.values())), 'shorted nets'
 for rr,c in components.items():
    if not re.match(r'^(R|C|Q|D|RV|L|TP|J)'+str(ch)+r'\d{2}$',rr):continue
    other=re.sub(r'\d+',lambda m:str(int(m[0])+100),rr) if ch==1 else None
    if other and other in components:
        for tag in ['value','footprint']:
            assert c.findtext(tag)==components[other].findtext(tag),(rr,other,tag)
for ref,c in components.items():
 fp=c.findtext('footprint');assert fp,'No footprint '+ref
 lib,name=fp.split(':',1)
 file=P/'MOSFETAmp2.pretty'/f'{name}.kicad_mod'if lib=='MOSFETAmp2'else Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')/(lib+'.pretty')/(name+'.kicad_mod')
 assert file.exists(),(ref,fp)
 pads=set(re.findall(r'\(pad "([^"]+)"',file.read_text()))
 pins={pin for rr,pin in actual if rr==ref};assert pins<=pads,(ref,pins,pads)
checks.append('All footprints exist and contain every connected numbered pad.')
assert (P/'MOSFETAmp2.kicad_pcb').read_bytes()==(P/'work/original/MOSFETAmp2.kicad_pcb').read_bytes()
checks.append('Original empty PCB preserved byte for byte.')
result={'status':'PASS','checks':len(checks),'components':len(components),'connected_pins':len(actual),'notes':checks}
(P/'work/connectivity_verification.json').write_text(json.dumps(result,indent=2))
print({k:v for k,v in result.items()if k!='notes'})
