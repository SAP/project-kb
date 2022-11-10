from client.cli.config_parser import get_configuration


def test_get_configuration():
    """Test get_configuration()"""
    config = get_configuration(None)
    print(config.__dict__)
    pass
