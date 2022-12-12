import pytest

from util.config_parser import get_configuration


@pytest.mark.skip(reason="Let's skip this for now")
def test_get_configuration():
    """Test get_configuration()"""
    config = get_configuration(None)
    assert config is not None
