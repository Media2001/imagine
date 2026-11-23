/* Current anonymous B01 UI proof, fixed local demo only. */
const {chromium} = require('playwright');
const fs = require('fs');
const path = require('path');
(async()=>{
 const root=__dirname, runtime=JSON.parse(fs.readFileSync(path.join(root,'runtime.json'),'utf8'));
 const base=runtime.base.replace(/\/$/,'');
 if(base!=='http://192.168.129.32:8085')throw Error('Forbidden browser target');
 const browser=await chromium.launch({headless:true});
 const ctx=await browser.newContext({viewport:{width:1440,height:1000},locale:'fr-FR'});
 const blocked=[];
 await ctx.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin!==base){blocked.push(u.origin);r.abort();}else r.continue();});
 const page=await ctx.newPage(); const records=[];
 const cases=[['accueil','/'],['kiosque','/numeros/'],['numero',new URL(runtime.issues[0].url).pathname],['article-ouvert','/demo-2026-t1-ouvert/'],['article-reserve','/demo-2026-t1-reserve-1/'],['thematique',new URL(runtime.themes[0].url).pathname],['agenda','/evenements/'],['evenement','/evenements/demo-events-2/'],['partenaires','/partenaires/'],['partenaire','/partenaires/demo-partners-2/'],['page','/calendrier-fictif/'],['recherche','/?s=fictif'],['recherche-vide','/?s=b01-aucun-resultat-xyz'],['404','/b01-page-inexistante-xyz/'],['index','/?post_type=post']];
 fs.mkdirSync(path.join(root,'captures'),{recursive:true});
 const capture=async(name,url,width)=>{
  await page.setViewportSize({width,height:1000});
  const response=await page.goto(base+url,{waitUntil:'networkidle'});
  const metrics=await page.evaluate(()=>({h1:document.querySelectorAll('h1').length,mention:document.body.textContent.includes('squelette, sans habillage'),width:innerWidth,scrollWidth:document.documentElement.scrollWidth,background:getComputedStyle(document.body).backgroundColor,color:getComputedStyle(document.body).color,locale:document.documentElement.lang}));
  const file='captures/'+name+'.png'; await page.screenshot({path:path.join(root,file),fullPage:true});
  const ok=metrics.h1===1&&metrics.mention&&metrics.scrollWidth<=width&&response.status()===(name.startsWith('404')?404:200);
  records.push({name,url:base+url,status:response.status(),metrics,file,ok});
 };
 for(const [name,url]of cases)await capture(name+'-desktop',url,1440);
 for(const [name,url]of [['accueil','/'],['article-ouvert','/demo-2026-t1-ouvert/'],['article-reserve','/demo-2026-t1-reserve-1/'],['page','/calendrier-fictif/']])await capture(name+'-mobile',url,390);
 const checks=[];
 await page.goto(base+'/',{waitUntil:'networkidle'});await page.keyboard.press('Tab');
 checks.push({name:'skip link first keyboard target',ok:await page.evaluate(()=>document.activeElement.getAttribute('href')==='#imagine-main')});
 await page.keyboard.press('Enter');checks.push({name:'skip link focuses main',ok:await page.evaluate(()=>document.activeElement.id==='imagine-main')});
 await page.goto(base+'/demo-2026-t1-ouvert/',{waitUntil:'networkidle'});checks.push({name:'open full article',ok:(await page.locator('[data-imagine-body="article"]').textContent()).includes('Scène fictive 5.')});
 await page.goto(base+'/demo-2026-t1-reserve-1/',{waitUntil:'networkidle'});checks.push({name:'current reserved response no body',ok:!(await page.content()).includes('CONTENU_FICTIF_RESERVE_')});
 await page.goto(base+'/',{waitUntil:'networkidle'});await page.locator('input[name="s"]').fill('b01-aucun-resultat-xyz');await Promise.all([page.waitForURL('**/?s=b01-aucun-resultat-xyz'),page.locator('input[name="s"]').press('Enter')]);await page.waitForLoadState('networkidle');checks.push({name:'native GET search and precise empty message',ok:new URL(page.url()).searchParams.get('s')==='b01-aucun-resultat-xyz'&&(await page.locator('main').textContent()).includes('Aucun résultat pour votre recherche.')});
 fs.writeFileSync(path.join(root,'browser.json'),JSON.stringify({at:new Date().toISOString(),scope:'imagine-test-demo',browser:browser.version(),playwright:require('playwright/package.json').version,blockedOrigins:[...new Set(blocked)],records,checks,passed:records.every(r=>r.ok)&&checks.every(r=>r.ok)},null,2));
 await browser.close();
 console.log(JSON.stringify({captures:records.length,checks:checks.length,failed:[...records,...checks].filter(r=>!r.ok)},null,2));
 if([...records,...checks].some(r=>!r.ok))process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
