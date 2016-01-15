from mock import patch, MagicMock, ANY, call

from mies.senses.smell.smell_propagator import propagate_smell_around_source


def test_propagate_smell_around_source():
    cache = MagicMock()
    strength = 5
    address = "g-b(90,41)-l0-b(14,0)-l0-b(46,66)"
    x, y = 46, 66
    count = 100
    key = "CURRENT_SMELLS.abc123"

    with patch('mies.senses.smell.smell_propagator.add_smell_to_bldg_and_containers') \
            as add_smell_mock:
        add_smell_mock.return_value = 1

        result = propagate_smell_around_source(address, cache, count, key,
                                               strength, x, y)

    assert result == 169
    assert add_smell_mock.call_count == 69

    calls = [call('g-b(90,41)-l0-b(14,0)-l0-b(42,64)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(42,65)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(42,66)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(42,67)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(42,68)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(43,63)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(43,64)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(43,65)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(43,66)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(43,67)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(43,68)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(43,69)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(44,62)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(44,63)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(44,64)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(44,65)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(44,66)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(44,67)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(44,68)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(44,69)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(44,70)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(45,62)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(45,63)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(45,64)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(45,65)', ANY, key, 4),
             call('g-b(90,41)-l0-b(14,0)-l0-b(45,66)', ANY, key, 4),
             call('g-b(90,41)-l0-b(14,0)-l0-b(45,67)', ANY, key, 4),
             call('g-b(90,41)-l0-b(14,0)-l0-b(45,68)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(45,69)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(45,70)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(46,62)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(46,63)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(46,64)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(46,65)', ANY, key, 4),
             call('g-b(90,41)-l0-b(14,0)-l0-b(46,66)', ANY, key, 5),
             call('g-b(90,41)-l0-b(14,0)-l0-b(46,67)', ANY, key, 4),
             call('g-b(90,41)-l0-b(14,0)-l0-b(46,68)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(46,69)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(46,70)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(47,62)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(47,63)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(47,64)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(47,65)', ANY, key, 4),
             call('g-b(90,41)-l0-b(14,0)-l0-b(47,66)', ANY, key, 4),
             call('g-b(90,41)-l0-b(14,0)-l0-b(47,67)', ANY, key, 4),
             call('g-b(90,41)-l0-b(14,0)-l0-b(47,68)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(47,69)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(47,70)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(48,62)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(48,63)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(48,64)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(48,65)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(48,66)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(48,67)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(48,68)', ANY, key, 3),
             call('g-b(90,41)-l0-b(14,0)-l0-b(48,69)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(48,70)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(49,63)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(49,64)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(49,65)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(49,66)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(49,67)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(49,68)', ANY, key, 2),
             call('g-b(90,41)-l0-b(14,0)-l0-b(49,69)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(50,64)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(50,65)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(50,66)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(50,67)', ANY, key, 1),
             call('g-b(90,41)-l0-b(14,0)-l0-b(50,68)', ANY, key, 1)]

    add_smell_mock.assert_has_calls(calls, any_order=True)
