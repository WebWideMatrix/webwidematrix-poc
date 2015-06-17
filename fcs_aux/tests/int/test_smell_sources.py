from mies.senses.smell.smell_source import set_smell_source, get_smell_sources


def test_set_smell_source(bldg_addresses_on_same_flr):
    for addr in bldg_addresses_on_same_flr:
        set_smell_source(addr, 100)
    for smell_sources in get_smell_sources():
        for smell in smell_sources:
            assert smell == 100
