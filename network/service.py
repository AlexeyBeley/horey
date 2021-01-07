"""
L3-L4 Service module
"""


class Service:
    """
    Main class to represent API to services.
    """
    ANY = None

    @classmethod
    def any(cls):
        """
        Get Any service
        :return:
        """
        if Service.ANY is None:
            Service.ANY = Service()
        return Service.ANY

    def __init__(self):
        pass

    def __str__(self):
        if self is Service.any():
            return "any"
        raise NotImplementedError()

    def copy(self):
        """
        Copy object
        :return:
        """
        if self is self.any():
            return self.any()

        raise NotImplementedError()

    def intersect(self, other):
        """
        Intersect 2 services.
        :param other:
        :return:
        """
        if not isinstance(other, Service):
            raise ValueError()
        raise NotImplementedError(self)


class ServiceTCP(Service):
    """TCP family services"""

    def __init__(self):
        super().__init__()
        self.start = None
        self.end = None

    def __str__(self):
        return "TCP:[{}-{}]".format(self.start, self.end)

    def copy(self):
        """
        Make a copy of self
        :return:
        """
        service = ServiceTCP()
        service.start = self.start
        service.end = self.end
        return service


class ServiceUDP(Service):
    """
    UDP family services
    """
    def __init__(self):
        super().__init__()
        self.start = None
        self.end = None

    def __str__(self):
        return "UDP:[{}-{}]".format(self.start, self.end)

    def copy(self):
        """Make a copy of self"""
        service = ServiceUDP()
        service.start = self.start
        service.end = self.end
        return service
