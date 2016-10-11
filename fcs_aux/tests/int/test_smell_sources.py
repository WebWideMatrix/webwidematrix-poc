from mies.senses.smell.smell_source import create_smell_source, get_smell_sources


def test_set_smell_source(bldg_addresses_on_same_flr):
    # TODO at least change the redis db
    for addr in bldg_addresses_on_same_flr:
        create_smell_source(addr, 100)
    for smell in get_smell_sources():
        assert smell == 100
