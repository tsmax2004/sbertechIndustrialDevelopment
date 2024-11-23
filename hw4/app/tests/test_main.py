import pytest
from unittest.mock import MagicMock
from ..src.main import get, inc, Storage


class FakeStorage(Storage):
    def __init__(self):
        self.value = 0

    def inc(self):
        self.value += 1
        return self.value

    def get(self):
        return self.value


@pytest.fixture
def mock_storage(mocker):
    mocker.patch('app.src.main.make_storage', MagicMock(return_value=FakeStorage()))


def test_get(mock_storage):
    assert get() == f'Текущее значение: {0}'
    assert get() == f'Текущее значение: {0}'


def test_inc(mock_storage):
    assert inc() == f'Текущее значение: {1}'
    assert get() == f'Текущее значение: {1}'
    assert inc() == f'Текущее значение: {2}'
