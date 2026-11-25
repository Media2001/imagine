"""Preparation only: official public ZIPs. No site, no PHP, no credentials."""
import hashlib,json,pathlib,urllib.request
OUT=pathlib.Path(__file__).resolve().parents[3]/'production/A-04/dependances'
SOURCES={'wordpress-6.9.1.zip':'https://wordpress.org/wordpress-6.9.1.zip','wordpress-7.0.zip':'https://wordpress.org/wordpress-7.0.zip','woocommerce-11.0.1.zip':'https://downloads.wordpress.org/plugin/woocommerce.11.0.1.zip'}
def main():
    OUT.mkdir(parents=True,exist_ok=True);results=[]
    for name,url in SOURCES.items():
        target=OUT/name
        try:
            if not target.exists():
                with urllib.request.urlopen(url,timeout=90) as source,target.open('xb') as out:
                    size=0
                    while block:=source.read(1048576):
                        size+=len(block)
                        if size>150000000:raise RuntimeError('PUBLIC_SIZE_LIMIT')
                        out.write(block)
            with target.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
            results.append({'name':name,'url':url,'sha256':sha,'bytes':target.stat().st_size,'ok':True})
        except Exception as e:results.append({'name':name,'url':url,'ok':False,'class':type(e).__name__,'code':getattr(e,'code',None)})
    (OUT/'public.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
    return int(any(not x['ok'] for x in results))
if __name__=='__main__':raise SystemExit(main())
