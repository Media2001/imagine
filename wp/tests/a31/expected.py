"""Expected fictional counts, not native evidence or a business implementation."""


def expected(repeats):
    if repeats == 1:
        return {'years': {'groups': [{'year': 2020, 'count': 8}], 'autres': 2},
                'statuses': {'groups': [{'year': 2020, 'status': 'completed', 'count': 7}], 'autres': 3},
                'natures': {'groups': [{'nature': 'illisible', 'count': 2}, {'nature': 'none', 'count': 2},
                                        {'nature': 'parent', 'count': 1}, {'nature': 'renewal', 'count': 3},
                                        {'nature': 'resubscribe', 'count': 1}, {'nature': 'switch', 'count': 1}], 'autres': 0}, 'orphan_renewals': 1,
                'living_without_parent': 1, 'orders_missing_account': 1, 'orders_link_unknown': 0,
                'refunds': {'total': 1, 'groups': [{'year': 2021, 'count': 1}], 'autres': 0},
                'oldest_year': 'fusionne'}
    assert repeats == 5
    return {'years': {'groups': [{'year': 2017, 'count': 5}, {'year': 2019, 'count': 5}, {'year': 2020, 'count': 40}], 'autres': 0},
            'statuses': {'groups': [{'year': 2017, 'status': 'completed', 'count': 5},
                                    {'year': 2019, 'status': 'completed', 'count': 5},
                                    {'year': 2020, 'status': 'autre', 'count': 5},
                                    {'year': 2020, 'status': 'completed', 'count': 35}], 'autres': 0},
            'natures': {'groups': [{'nature': 'illisible', 'count': 10}, {'nature': 'none', 'count': 10},
                                   {'nature': 'parent', 'count': 5}, {'nature': 'renewal', 'count': 15},
                                   {'nature': 'resubscribe', 'count': 5}, {'nature': 'switch', 'count': 5}], 'autres': 0},
            'orphan_renewals': 5, 'living_without_parent': 5, 'orders_missing_account': 5, 'orders_link_unknown': 0,
            'refunds': {'total': 5, 'groups': [{'year': 2021, 'count': 5}], 'autres': 0}, 'oldest_year': 2017}
