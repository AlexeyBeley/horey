"""
DNS records representation
"""


class DNS:
    """
    Main class to represent dns record.
    """
    def __init__(self, fqdn):
        self.fqdn = fqdn

    def __str__(self):
        return self.fqdn

    def __eq__(self, other):
        if not isinstance(other, DNS):
            return False
        if self.fqdn != other.fqdn:
            return False

        return True

    def copy(self):
        """
        Copy dns record
        :return:
        """
        return DNS(self.fqdn)
