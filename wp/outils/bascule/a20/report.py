"""Closed A20 report contract; untrusted PHP output is never echoed."""
import hashlib
import json
from pathlib import Path
import re

HERE=Path(__file__).resolve().parent
CONTRACT=json.loads((HERE/'report-contract.json').read_text(encoding='utf-8'))
HEADER='# Récurrences enregistrées — lecture seule\n\nComptes uniquement ; aucune correspondance ni decision de tarif.\n\n```json\n'
STATES={'active','pending','on-hold','pending-cancel'}

def require(ok):
    if not ok:raise RuntimeError('A20_REPORT_INVALID')

def keys(value,expected):
    require(type(value) is dict and set(value)==set(expected))

def number(value,low=0,high=None):
    require(type(value) is int and value>=low and (high is None or value<=high))

def no_duplicates(pairs):
    result={}
    for key,value in pairs:
        require(key not in result);result[key]=value
    return result

def validate(output,audit):
    try:
        _validate(output,audit)
    except Exception:
        raise RuntimeError('A20_REPORT_INVALID') from None

def _validate(output,audit):
    require(not output.is_symlink() and output.is_dir() and set(p.name for p in output.iterdir())=={'tarifs.json','tarifs.md'})
    for name in ['tarifs.json','tarifs.md']:
        p=output/name
        require(not p.is_symlink() and p.is_file() and p.stat().st_nlink==1 and 0<p.stat().st_size<=16777216)
    raw=(output/'tarifs.json').read_bytes()
    data=json.loads(raw.decode('utf-8'),object_pairs_hook=no_duplicates)
    require((output/'tarifs.md').read_bytes()==HEADER.encode('utf-8')+raw+b'```\n')
    keys(data,['schema','read_only','storage','counts','scope','audit_sha256'])
    require(data['schema']==CONTRACT['schema'] and data['read_only'] is True and data['scope']==CONTRACT['scope'])
    photo=json.loads(audit.read_bytes())
    require(data['storage'] in ['classic','hpos'] and data['storage']==photo['sections']['commerce']['order_storage'])
    require(data['audit_sha256']==hashlib.sha256(audit.read_bytes()).hexdigest())
    v=data['counts'];keys(v,CONTRACT['count_keys'])
    require(v['definitions']==CONTRACT['definitions'])
    live=v['live_subscriptions'];number(live)
    for key in ['multiple_product_lines','without_product_line','with_fee_line','with_shipping_line','foreign_currency','zero_recurring_total']:
        number(v[key],high=live)
    require(type(v['products']) is list and type(v['countries']) is list)
    seen=[]
    for p in v['products']:
        keys(p,['product','variation','count','states','schedules','non_annual','amounts','other_amounts'])
        number(p['product']);number(p['variation']);number(p['count'],1,live)
        seen.append((p['product'],p['variation']))
        count=p['count'];keys(p['states'],STATES)
        for n in p['states'].values():number(n,high=count)
        require(sum(p['states'].values())==count)
        number(p['non_annual'],high=count);number(p['other_amounts'],high=count)
        require(type(p['schedules']) is list and type(p['amounts']) is list)
        schedule_keys=[];schedule_total=0;non_annual=0
        for row in p['schedules']:
            keys(row,['interval','period','count'])
            number(row['interval'],1);number(row['count'],1,count)
            require(row['period'] in ['day','week','month','year'])
            schedule_keys.append((row['period'],row['interval']));schedule_total+=row['count']
            if (row['period'],row['interval']) not in [('year',1),('month',12)]:non_annual+=row['count']
        require(schedule_keys==sorted(set(schedule_keys)) and schedule_total==count and non_annual==p['non_annual'])
        amount_keys=[];amount_total=p['other_amounts']
        for row in p['amounts']:
            keys(row,['currency','amount','count']);number(row['count'],5,count)
            require(type(row['currency']) is str and re.fullmatch('[A-Z]{3}',row['currency']) is not None)
            require(type(row['amount']) is str and re.fullmatch(r'-?(?:0|[1-9][0-9]{0,17})\.[0-9]{2,12}',row['amount']) is not None)
            amount_keys.append(row['currency']+':'+row['amount']);amount_total+=row['count']
        require(amount_keys==sorted(set(amount_keys)) and amount_total==count)
    require(seen==sorted(set(seen)))
    country_keys=[];country_total=0;shipping_total=0
    for row in v['countries']:
        keys(row,['country','count','with_shipping']);number(row['count'],5,live);number(row['with_shipping'],high=row['count'])
        require(type(row['country']) is str and row['country'] in CONTRACT['countries'])
        country_keys.append(row['country']);country_total+=row['count'];shipping_total+=row['with_shipping']
    require(country_keys==sorted(set(country_keys)))
    for key in ['other_countries','unknown_country']:
        row=v[key];keys(row,['count','with_shipping']);number(row['count'],high=live);number(row['with_shipping'],high=row['count'])
        country_total+=row['count'];shipping_total+=row['with_shipping']
    require(country_total==live and shipping_total==v['with_shipping_line'])
