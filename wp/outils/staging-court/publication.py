"""A-01 publication gate. Shared staging code and templates stay untouched."""
import re


def validate_name(name):
    if (not isinstance(name, str) or len(name) > 40
            or not re.fullmatch(r'imagine-test-[a-z0-9]+(?:-[a-z0-9]+)*', name)):
        raise ValueError('TEST_SITE_NAME_REQUIRED')
    return name


def guarded_publish(offline, inject, start, probe, stop=lambda: None):
    steps = offline.get('steps', [])
    accepted = (offline.get('data_verified') is True and isinstance(steps, list)
                and [s.get('phase') for s in steps] == ['neutraliser', 'anonymiser', 'verifier']
                and all(s.get('exit') == 0 and s.get('report', {}).get('ok') is True
                        and not s.get('report', {}).get('issues') for s in steps))
    if not accepted:
        return {'status': 'REFUSED_OFFLINE', 'full_staging_ready': False}
    try:
        inject()
        start()
        result = probe()
        if result.get('ok') is not True:
            stop()
        return {'status': 'verified' if result.get('ok') is True else 'REFUSED_RUNTIME',
                'full_staging_ready': result.get('ok') is True, 'probe': result}
    except Exception:
        stop()
        raise
