"""Independent fixture oracle, not extracted from the homepage or its WP_Query.
B00 seed and C08 seed explicitly date their articles 2026-01-01 12:00:00.
Resolve fixture identities from their manifests, then apply date DESC / ID DESC.
"""
FIXTURE_POST_DATE = '2026-01-01 12:00:00'


def latest_article_ids(manifest, rows, c08=None):
    # Enumerate authored fixture keys, never all keys merely matching a prefix.
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'wp/outils/demo'))
    from b00_fixtures import fixture_data
    keys = [issue['slug'] + suffix for issue in fixture_data()['issues']
            for suffix in ('-reserve-1', '-reserve-2', '-reserve-3', '-ouvert')]
    expected = {int(manifest[key]) for key in keys}
    if c08:
        expected.update(int(c08[key]) for key in ('article','automatique'))
    actual = [int(row['id']) for row in rows]
    if set(actual) != expected or len(actual) != len(expected):
        raise ValueError('Published article inventory differs from independent B00/C08 fixtures')
    if any(row['date'] != FIXTURE_POST_DATE for row in rows):
        raise ValueError('Fixture publication dates differ from seed contract')
    return sorted(expected, reverse=True)[:5]


def home_matches(actual, expected):
    return len(actual) == 5 and list(actual) == list(expected)
