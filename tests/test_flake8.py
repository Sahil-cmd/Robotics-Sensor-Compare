# tests/test_flake8.py

import pytest
from flake8.api import legacy as flake8

@pytest.mark.flake8
@pytest.mark.linter
def test_flake8():
    style_guide = flake8.get_style_guide(
        ignore=['E501', 'W503', 'E203'],
        max_line_length=88,
        show_source=True,
    )
    report = style_guide.check_files(['src'])

    total_errors = report.total_errors
    assert total_errors == 0, f'Flake8 found {total_errors} errors'

if __name__ == '__main__':
    test_flake8()
