"""
L3-L4 Service module
"""
import pdb


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

        if other is self.any():
            return self

        if self is self.any():
            return other

        if not isinstance(other, Service):
            raise ValueError()

        if type(self) != type(other):
            return False
        return self._intersect(other)

    def _intersect(self, other):
        raise NotImplementedError(other)


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

    def _intersect(self, other):
        if self.start > other.end:
            return False

        if self.end < other.start:
            return False

        return True


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

    def _intersect(self, other):
        if self.start > other.end:
            return False

        if self.end < other.start:
            return False

        return True


class ServiceICMP(Service):
    """
    ICMP family services
    """

    ANY = None

    @classmethod
    def any(cls):
        """
        Get Any ICMP service
        :return:
        """
        if ServiceICMP.ANY is None:
            ServiceICMP.ANY = ServiceICMP()
        return ServiceICMP.ANY

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "ICMP"

    def copy(self):
        """Make a copy of self"""
        raise NotImplementedError()

    def _intersect(self, other):
        raise NotImplementedError()


class ServiceRDP(Service):
    """
    ICMP family services
    """

    ANY = None

    @classmethod
    def any(cls):
        """
        Get Any ICMP service
        :return:
        """
        if ServiceRDP.ANY is None:
            ServiceRDP.ANY = ServiceRDP()
        return ServiceRDP.ANY

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "RDP"

    def copy(self):
        """Make a copy of self"""
        raise NotImplementedError()

    def _intersect(self, other):
        raise NotImplementedError()
