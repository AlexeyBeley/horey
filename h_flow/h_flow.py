"""
Module handling h_flow
"""


class HFlowFilter:
    """
    Filter representation
    """
    def __init__(self):
        self.src = self.TunnelEdgeFilter()
        self.dst = self.TunnelEdgeFilter()
        self.info = None

    def __str__(self):
        return "src:{}\ndst: {}".format(self.src, self.dst)

    class TunnelEdgeFilter:
        """
        Edge filter class
        """
        def __init__(self):
            self.ip = None
            self.service = None
            self.dns = None

        def __str__(self):
            return "{},{},{}".format(self.ip, self.dns, self.service)


class HFlow:
    """
    Class representing HFlow.
    """
    def __init__(self):
        self.tunnel = None
        self.end_point_src = None
        self.end_point_dst = None

    def __str__(self):
        ret = "{} -> {}\n".format(str(self.end_point_src), str(self.end_point_dst))
        ret += "\n{}".format(str(self.tunnel))
        return ret

    def apply_dst_filters_on_start(self, h_filters):
        """
        H_Flow filters on start
        :param h_filters:
        :return:
        """
        lst_ret = []
        for h_filter in h_filters:
            lst_ret += self.apply_dst_filter_on_start(h_filter)

        return lst_ret

    def apply_dst_filter_on_start(self, h_filter):
        """
        Dst filters on start
        :param h_filter:
        :return:
        """
        lst_ret = []

        for traffic_start, traffic_end in self.tunnel.traffic_start.apply_dst_filter(h_filter):
            if traffic_start is None or traffic_end is None:
                continue

            h_flow_ret = HFlow()
            h_flow_ret.end_point_src = self.end_point_src
            h_flow_ret.end_point_dst = self.end_point_dst
            h_flow_ret.tunnel = HFlow.Tunnel(traffic_start=traffic_start, traffic_end=traffic_end)
            lst_ret.append(h_flow_ret)

        return lst_ret

    def copy(self, copy_src_traffic_to_dst=False):
        """
        Deep copy flow.
        :param copy_src_traffic_to_dst:
        :return:
        """
        ret = HFlow()
        ret.tunnel = self.tunnel.copy(copy_src_traffic_to_dst=copy_src_traffic_to_dst)
        ret.end_point_src = self.end_point_src.copy()
        ret.end_point_dst = self.end_point_dst.copy()
        return ret

    class EndPoint:
        """
        Hflow endpoint- maybe src, maybe dst.
        This is abstract object representing hflow next stop.

        """
        def __init__(self):
            self._ip = None
            self._dns = None
            self.custom = {}

        @property
        def ip(self):
            """
            Ip address
            :return:
            """
            return self._ip

        @ip.setter
        def ip(self, ip):
            """
            Set ip address
            :param ip:
            :return:
            """
            if self._ip is not None:
                raise Exception("IP can be single instance")
            self._ip = ip

        @property
        def dns(self):
            """
            DNS address
            :return:
            """
            return self._dns

        @dns.setter
        def dns(self, dns):
            """
            DNS address setter
            :param dns:
            :return:
            """
            if self._dns is not None:
                raise Exception("IP can be single instance")
            self._dns = dns

        def add_custom(self, key, value):
            """

            :param key:
            :param value: if can include multiple destinations, should implement __add__
            :return:
            """
            if key in self.custom:
                self.custom[key].add(value)
            else:
                self.custom[key] = value

        def copy(self):
            """
            Deep copy of self
            :return:
            """
            ret = HFlow.EndPoint()
            if self.ip is not None:
                ret._ip = self.ip.copy()
            if self.dns is not None:
                ret._dns = self.dns.copy()

            ret.custom = self.custom

    class Tunnel:
        """
        Class representing H_Flow Tunnel
        """
        def __init__(self, traffic_start=None, traffic_end=None):
            self.traffic_start = traffic_start
            self.traffic_end = traffic_end

        def __str__(self):
            return "{} ==>\n==> {}".format(str(self.traffic_start), str(self.traffic_end))

        class Traffic:
            """
            Class representing a single traffic flow
            """
            ANY = None

            def __init__(self):
                self.ip_src = self.any()
                self.ip_dst = self.any()

                self.dns_src = self.any()
                self.dns_dst = self.any()

                self.service_src = self.any()
                self.service_dst = self.any()

            def __str__(self):
                return "[ip:{} , dns:{} , service:{} -> ip:{} , dns:{} , service:{}]".format(self.ip_src, self.dns_src, self.service_src, self.ip_dst, self.dns_dst, self.service_dst)

            def intersect(self, self_end_point, other_end_point):
                """
                Find intersection.
                :param self_end_point:
                :param other_end_point:
                :return:
                """
                if self_end_point is self.any():
                    return other_end_point
                return self_end_point.intersect(other_end_point)

            def apply_dst_filter(self, h_filter):
                """
                Apply the filter on destination.
                :param h_filter:
                :return:
                """
                ip_src_intersect = self.intersect(self.ip_src, h_filter.ip_src)
                if ip_src_intersect is None:
                    return []

                service_src_intersect = self.intersect(self.service_src, h_filter.service_src)
                if service_src_intersect is None:
                    return []

                ip_dst_intersect = self.intersect(self.ip_dst, h_filter.ip_dst)
                if ip_dst_intersect is None:
                    return []

                service_dst_intersect = self.intersect(self.service_dst, h_filter.service_dst)
                if service_dst_intersect is None:
                    return []

                traffic_start = self.copy()
                traffic_start.ip_src = ip_src_intersect
                traffic_start.service_src = service_src_intersect

                if h_filter.dns_src != self.dns_src:
                    raise NotImplementedError("Don't know what towrite here")

                if h_filter.dns_dst != self.dns_dst:
                    raise NotImplementedError("Don't know what towrite here")

                traffic_end = HFlow.Tunnel.Traffic()
                traffic_end.ip_src = traffic_start.ip_src
                traffic_end.dns_src = traffic_start.dns_src
                traffic_end.service_src = traffic_start.service_src

                traffic_end.ip_dst = ip_dst_intersect
                traffic_end.dns_dst = traffic_start.dns_dst
                traffic_end.service_dst = service_dst_intersect
                return [(traffic_start, traffic_end)]

            def copy(self):
                """
                Deep copy of self.
                :return:
                """
                ret = HFlow.Tunnel.Traffic()

                if self.ip_src is not None:
                    ret.ip_src = self.ip_src.copy()

                if self.dns_src is not None:
                    ret.dns_src = self.dns_src.copy()

                if self.ip_dst is not None:
                    ret.ip_dst = self.ip_dst.copy()

                if self.dns_dst is not None:
                    ret.dns_dst = self.dns_dst.copy()

                if self.service_src is not None:
                    ret.service_src = self.service_src.copy()

                if self.service_dst is not None:
                    ret.service_dst = self.service_dst.copy()

                return ret

            @staticmethod
            def any():
                """
                Return singleton ANY
                :return:
                """
                if HFlow.Tunnel.Traffic.ANY is None:
                    HFlow.Tunnel.Traffic.ANY = HFlow.Tunnel.Traffic.Any()
                return HFlow.Tunnel.Traffic.ANY

            class Any:
                """
                Class representing singleton ANY
                """
                def __str__(self):
                    return "any"

                @staticmethod
                def copy():
                    """
                    Deep copy
                    :return:
                    """

                    return HFlow.Tunnel.Traffic.ANY

                @staticmethod
                def intersect(other):
                    """
                    Intersect of ANY - is the src object
                    :param other:
                    :return:
                    """
                    return other

        def copy(self, copy_src_traffic_to_dst=False):
            """
            Deep copy of self
            :param copy_src_traffic_to_dst:
            :return:
            """
            ret = HFlow.Tunnel()
            ret.traffic_start = self.traffic_start.copy()

            if copy_src_traffic_to_dst:
                ret.traffic_end = self.traffic_start.copy()
            else:
                ret.traffic_end = self.traffic_end.copy()

            return ret

        def repr_in(self):
            """
            Readable representation of in
            :return:
            """
            return "[ip:{} , dns:{} , service:{}]".format(self.traffic_start.ip_src, self.traffic_start.dns_src, self.traffic_start.service_src)

        def repr_out(self):
            """
            Readable representation of out
            :return:
            """
            return "[ip:{} , dns:{} , service:{}]".format(self.traffic_start.ip_dst, self.traffic_start.dns_dst, self.traffic_start.service_dst)
