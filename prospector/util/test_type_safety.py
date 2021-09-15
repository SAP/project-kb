from util.type_safety import is_instance_of_either


def test_is_instance_of_either():
    assert is_instance_of_either([0, 1, 2, 3], int) is True
    assert is_instance_of_either(["0", 1, 2, 3], int) is False
    assert is_instance_of_either([1.34, 2.2, 3.5], float) is True
    assert is_instance_of_either([1.34, 2.2, "3.5"], float) is False
    assert is_instance_of_either([1, 2.2, 3.5, 42], int, float) is True
