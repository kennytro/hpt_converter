import pytest
from pathlib import Path

@pytest.fixture
def data_root(request) -> Path:
    return Path(request.config.rootdir).joinpath('tests', 'data').resolve()
