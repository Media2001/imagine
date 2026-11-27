"""Expected fictional counts, not native evidence or a business implementation."""


def expected(repeats):
    if repeats == 1:
        return {'years': {'groups': [{'year': 2020, 'count': 8}], 'autres': 2},
                'statuses': {'groups': [{'year': 2020, 'status': 'completed', 'count': 7}], 'autres': 3},
                'natures': {'groups': [], 'autres': 10}, 'orphan_renewals': {'groups': [], 'autres': 1},
                'structural_links': {'groups': [], 'autres': 2}, 'refunds': {'groups': [], 'autres': 1},
                'oldest_year': 'fusionne'}
    assert repeats == 5
    return {'years': {'groups': [{'year': 2018, 'count': 5}, {'year': 2019, 'count': 5}, {'year': 2020, 'count': 40}], 'autres': 0},
            'statuses': {'groups': [{'year': 2018, 'status': 'completed', 'count': 5},
                                    {'year': 2019, 'status': 'completed', 'count': 5},
                                    {'year': 2020, 'status': 'autre', 'count': 5},
                                    {'year': 2020, 'status': 'completed', 'count': 35}], 'autres': 0},
            'natures': {'groups': [{'nature': 'illisible', 'count': 10}, {'nature': 'none', 'count': 15},
                                   {'nature': 'parent', 'count': 5}, {'nature': 'renewal', 'count': 10},
                                   {'nature': 'resubscribe', 'count': 5}, {'nature': 'switch', 'count': 5}], 'autres': 0},
            'orphan_renewals': {'groups': [{'metric': 'renewals_missing_subscription', 'count': 5}], 'autres': 0},
            'structural_links': {'groups': [{'metric': 'living_without_parent', 'count': 5},
                                            {'metric': 'orders_missing_account', 'count': 5}], 'autres': 0},
            'refunds': {'groups': [{'year': 2021, 'count': 5}], 'autres': 0}, 'oldest_year': 2018}
