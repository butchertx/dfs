from typing import Dict, List, Callable

"""
Structure for contest_reqs:
- first level is named groups of contests
"""
PROPS_BOOL = [
    'guaranteed',
    'double_up'
]

PROPS_INT = [
    'multientry'
]

PROPS_FLOAT_RANGE = [
    'max_entry_fee'
]

PROPS_DOW = [
    'day'
]

contest_reqs = {
    "thursday single-entry showdown double-ups": {
        "guaranteed": True,
        "double_up": True,
        "multientry": 1,
        "max_entry_fee": [0., 5.],  # this is a range
        "day": 'Thursday',
        "this_week": True
    }
}


def translate_bool(name: str, value: bool):
    if value:
        return f'AND {name}\n'
    else:
        return f'AND NOT {name}\n'


def translate_int(name: str, value: int):
    return f'AND {name}={value}\n'


def translate_float_range(name: str, range: List[float]) -> str:
    # assert(len(range) == 2, f'Float range must only have two values! {range}')
    return f'AND {name} <= {range[1]}\nAND {name} >= {range[0]}\n'


def make_where_strings(props: Dict, props_list: List[str], props_converter: Callable) -> str:
    where_string = ''
    for prop in props_list:
        if prop in props.keys():
            if props[prop]:
                where_string += props_converter(prop, props[prop])

    return where_string


def props_to_query(props: Dict):
    and_string = ''
    and_string += make_where_strings(props, PROPS_BOOL, translate_bool)[4:]
    and_string += make_where_strings(props, PROPS_INT, translate_int)
    and_string += make_where_strings(props, PROPS_FLOAT_RANGE, translate_float_range)

    query = f'SELECT * FROM contests WHERE {and_string}'
    return query


if __name__ == "__main__":
    for prop_group in contest_reqs.keys():
        query = props_to_query(contest_reqs[prop_group])
        print(prop_group)
        print(query)
