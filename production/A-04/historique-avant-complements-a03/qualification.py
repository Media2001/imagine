"""Additive A04 qualification; never rewrites an A03 report/verdict.
Only a single newly scheduled native Woo administrative job is expected.
"""
import copy
import datetime

HOOK = 'woocommerce_run_on_woocommerce_admin_updated'
REASON = 'Woo schedules its administrative version-update handler; operational work is preserved, not executed.'

def qualify(before, after, targets):
    a=copy.deepcopy(before);b=copy.deepcopy(after);expected=[]
    result={'schema':'imagine-a04-qualification-v1','qualified':False,'expected_hooks':expected,'native_a03_verdict_unchanged':True}
    try:
        for key,target in targets.items():
            if b['versions'][key] != target:return result
            b['versions'][key]=a['versions'][key]
        added=set(b['actions'])-set(a['actions'])
        permitted=[k for k in added if b['actions'][k]['hook']==HOOK]
        if len(permitted)>1:return result
        for key in permitted:
            if before['versions']['woocommerce']==after['versions']['woocommerce']:return result
            row=b['actions'][key]
            scheduled=datetime.datetime.strptime(row['date'],'%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc)
            start=datetime.datetime.fromisoformat(before['generated_at_utc']);end=datetime.datetime.fromisoformat(after['generated_at_utc'])
            if not start<=scheduled<=end:return result
            day=HOOK+':'+row['date'][:10]
            if b['action_days'].get(day,0)!=a['action_days'].get(day,0)+1:return result
            del b['actions'][key]
            if day in a['action_days']:b['action_days'][day]=a['action_days'][day]
            else:del b['action_days'][day]
            expected.append({'hook':HOOK,'action_id':int(key),'reason':REASON})
        a.pop('generated_at_utc',None);b.pop('generated_at_utc',None)
        result['qualified']=a==b
        return result
    except (KeyError,TypeError,ValueError):
        return result
