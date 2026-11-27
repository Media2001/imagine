"""Onze mutations bornées dans une copie jetable hors réseau, jamais sur le site."""
import sys
sys.dont_write_bytecode=True
import contextlib,hashlib,io,json,re
import c27
label=sys.argv[1]
rows=[]
for mutation in ['avant-paiement','tiers','operateur','source-ecrasee','export','effacement','export-tiers','reglage-invalide','source-lecture-incertaine','effacement-cache','vue-effacee']:
    with contextlib.redirect_stdout(io.StringIO()):
        status=c27.local(label+'-'+mutation,mutation)
    path=c27.PROOF/(label+'-'+mutation+'.log')
    text=path.read_text(encoding='utf-8')
    match=re.search(r'Tests: (\d+), Assertions: (\d+), Failures: (\d+)\.',text)
    detected=status==1 and match is not None and int(match[1])==12 and int(match[3])>0 and 'ERRORS!' not in text
    rows.append({'mutation':mutation,'exit':status,'detected':detected,'tests':int(match[1]) if match else None,'failures':int(match[3]) if match else None,'log':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    print(mutation,status,detected)
c27.save(label,{'mutations':rows,'count':len(rows),'detected':sum(r['detected'] for r in rows)})
assert len(rows)==11 and all(r['detected'] for r in rows)
