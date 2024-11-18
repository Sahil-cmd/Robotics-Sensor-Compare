import pytest
import os
from scspell import Report, SCSPELL_BUILTIN_DICT, spell_check

@pytest.fixture(scope='module')
def known_words():
    with open('spell_check.words', 'r') as f:
        return f.read().splitlines()

@pytest.mark.linter
def test_spell_check(known_words):
    source_files = []
    for root, _, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                source_files.append(os.path.join(root, file))

    report = Report(known_words)
    spell_check(
        source_files, base_dicts=[SCSPELL_BUILTIN_DICT],
        report_only=report, additional_extensions=[('', 'Python')]
    )

    unknown_word_count = len(report.unknown_words)
    assert unknown_word_count == 0, \
        f'Found {unknown_word_count} unknown words: ' + \
        ', '.join(sorted(report.unknown_words))

    unused_known_words = set(known_words) - report.found_known_words
    unused_known_word_count = len(unused_known_words)
    assert unused_known_word_count == 0, \
        f'{unused_known_word_count} words in the word list are not used: ' + \
        ', '.join(sorted(unused_known_words))

@pytest.mark.linter
def test_spell_check_word_list_order(known_words):
    assert known_words == sorted(known_words), \
        'The word list should be ordered alphabetically'

@pytest.mark.linter
def test_spell_check_word_list_duplicates(known_words):
    assert len(known_words) == len(set(known_words)), \
        'The word list should not contain duplicates'
