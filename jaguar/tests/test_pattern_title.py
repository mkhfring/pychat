from jaguar.validators import TITLE_PATTERN as pattern


def test_date_pattern():
    assert pattern.match('First Room')
    assert pattern.match('First-Room')
    assert pattern.match('First Sample-Room')
    assert pattern.match('Title with ?><!:; and ...')
    assert pattern.match('1')

    assert not pattern.match(' Title with Space in starting')
    assert not pattern.match('  Title with more than one Space in starting')
    assert not pattern.match('      Title with Tab in starting')
    assert not pattern.match('\nTitle with Enter in starting')
    assert not pattern.match('Title with Space in ending ')
    assert not pattern.match('Title with more than one Space in ending  ')
    assert not pattern.match('Title with Tab in ending      ')
    assert not pattern.match('Title with Enter in ending \n')

