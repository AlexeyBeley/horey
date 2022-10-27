from horey.pip_api.requirement import Requirement


def test_init():
    requirement = Requirement("test")
    assert isinstance(requirement, Requirement)


def test_init_equal():
    requirement = Requirement("test==1.0.0")


def test_init_less_equal():
    requirement = Requirement("test<=1.0.0")


def test_init_more_equal():
    requirement = Requirement("test>=1.0.0")


def test_init_more():
    requirement = Requirement("test>1.0.0")


def test_init_less():
    requirement = Requirement("test<1.0.0")


if __name__ == "__main__":
    test_init()
    test_init_equal()
    test_init_less_equal()
    test_init_more_equal()
    test_init_more()
    test_init_less()
