"""A-01 publication gate. Shared staging code and templates stay untouched."""


def guarded_publish(offline, inject, start, probe, stop=lambda: None):
    if offline.get('data_verified') is not True:
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
