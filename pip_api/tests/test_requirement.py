"""
Test Requirement

"""

from horey.pip_api.requirement import Requirement

# pylint: disable=missing-function-docstring


def test_init():
    requirement = Requirement("test")
    assert isinstance(requirement, Requirement)


def test_init_equal():
    requirement = Requirement("test==1.0.0")
    assert requirement.name == "test"
    assert requirement.min_version == "1.0.0"
    assert requirement.max_version == "1.0.0"
    assert requirement.include_min
    assert requirement.include_max


def test_init_less_equal():
    requirement = Requirement("test<=1.0.0")
    assert requirement.name == "test"
    assert requirement.min_version is None
    assert requirement.max_version == "1.0.0"
    assert requirement.include_min is None
    assert requirement.include_max


def test_init_more_equal():
    requirement = Requirement("test>=1.0.0")
    assert requirement.name == "test"
    assert requirement.min_version == "1.0.0"
    assert requirement.max_version is None
    assert requirement.include_min
    assert requirement.include_max is None


def test_init_more():
    requirement = Requirement("test>1.0.0")
    assert requirement.name == "test"
    assert requirement.min_version == "1.0.0"
    assert requirement.max_version is None
    assert requirement.include_min is False
    assert requirement.include_max is None


def test_init_less():
    requirement = Requirement("test<1.0.0")
    assert requirement.name == "test"
    assert requirement.min_version is None
    assert requirement.max_version == "1.0.0"
    assert requirement.include_min is None
    assert requirement.include_max is False


def test_generate_install_string():
    for test_string in [
        "test<1.0.0",
        "test>1.0.0",
        "test<=1.0.0",
        "test>=1.0.0",
        "test==1.0.0",
    ]:
        print(f"test_string: '{test_string}'")
        requirement = Requirement(test_string)
        assert requirement.generate_install_string() == test_string


if __name__ == "__main__":
    test_init()
    test_init_equal()
    test_init_less_equal()
    test_init_more_equal()
    test_init_more()
    test_init_less()
    test_generate_install_string()
