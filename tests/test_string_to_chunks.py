from raven_sh import string_to_chunks


def test_string_to_chunks_empty():
    assert string_to_chunks('foo', None) == {}
    assert string_to_chunks('foo', '') == {}


def test_string_to_chunks_short():
    assert string_to_chunks('foo', 'value', max_chars=6) == {'foo': 'value'}


def test_string_to_chunks_long_line():
    src = 'value\n' + 'a' * 100
    expected = {
        'foo0': 'value',
        'foo1': 'a' * 100,
    }
    assert string_to_chunks('foo', src, max_chars=12) == expected


def test_string_to_chunks_many_lines():
    src = 'value\n' * 22
    expected = {
        'foo00': 'value\nvalue',
        'foo01': 'value\nvalue',
        'foo02': 'value\nvalue',
        'foo03': 'value\nvalue',
        'foo04': 'value\nvalue',
        'foo05': 'value\nvalue',
        'foo06': 'value\nvalue',
        'foo07': 'value\nvalue',
        'foo08': 'value\nvalue',
        'foo09': 'value\nvalue',
        'foo10': 'value\nvalue',
    }
    assert string_to_chunks('foo', src, max_chars=12) == expected
