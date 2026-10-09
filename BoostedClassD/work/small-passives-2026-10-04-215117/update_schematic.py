import pathlib,re,shutil,json,hashlib
w=pathlib.Path(__file__).resolve().parent;dest=w/'review';dest.mkdir(exist_ok=True)
for f in (w/'backup').iterdir():
 if f.suffix in ['.kicad_sch','.kicad_pro','.kicad_sym'] or f.name.endswith('lib-table'):shutil.copy2(f,dest/f.name)
s=(dest/'Amplifiers.kicad_sch').read_text();changes={}
def update(m):
 b=m.group();ref=re.search(r'\(property "Reference" "(C\d+)"',b)
 if not ref or not 13<=int(ref[1][1:])<=24:return b
 r=ref[1];i=int(r[1:]);mpn='CL03A104KA3NNNC' if i in [13,14,17,18] else ('CL03A105MP3NSNC' if i in [15,16,19,20] else 'CL03A225MP3CRNC')
 voltage='25V' if i in [13,14,17,18] else '10V';lcsc={'CL03A104KA3NNNC':'C307379','CL03A105MP3NSNC':'C170153','CL03A225MP3CRNC':'C318539'}[mpn]
 value=re.search(r'\(property "Value" "([^"]+)"',b)[1];url='https://product.samsungsem.com/mlcc/'+mpn[:-1]+'.do'
 fields={'Footprint':'Capacitor_SMD:C_0201_0603Metric','Datasheet':url,'Rating':value+' / '+voltage+' X5R','Manufacturer':'Samsung Electro-Mechanics','MPN':mpn,'LCSC':lcsc}
 at=re.search(r'\(at ([^\)]+)\)',b)[1]
 for name,val in fields.items():
  pattern=r'(\(property "'+name+r'" ")[^"]*(")'
  if re.search(pattern,b):b=re.sub(pattern,lambda m:m[1]+val+m[2],b,count=1)
  else:
   prop='\n\t\t(property "'+name+'" "'+val+'" (at '+at+') (hide yes) (effects (font (size 1.27 1.27))))'
   b=b[:-3]+prop+'\n\t)'
 changes[r]={'value':value,'MPN':mpn,'LCSC':lcsc,'voltage':voltage,'package_metric':'0603','datasheet':url}
 return b
s=re.sub(r'\n\t\(symbol\n.*?\n\t\)',update,s,flags=re.S);assert len(changes)==12
(dest/'Amplifiers.kicad_sch').write_text(s);shutil.copy2(w/'candidate.kicad_pcb',dest/'BoostedClassD.kicad_pcb');(w/'parts.json').write_text(json.dumps(changes,indent=2))
print('Updated',len(changes),'capacitor footprints and sourcing fields in isolated hierarchical project')
h=json.loads((w/'baseline-hashes.json').read_text());print('Source changes since backup:',[n for n,v in h.items() if hashlib.sha256(pathlib.Path(n).read_bytes()).hexdigest()!=v])
