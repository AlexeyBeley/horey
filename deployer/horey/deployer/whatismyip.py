try:
    import dns
    import dns.resolver
except Exception as inst:
    print(repr(inst))


def fetch_ip_from_google():
    ns_address, query_address = 'ns1.google.com', 'o-o.myaddr.l.google.com'
    resolver = dns.resolver.Resolver(configure=True)

    resp = resolver.resolve(ns_address)

    ns_ip = resp[0].to_text()
    resolver.nameservers = [ns_ip]

    resp_two = resolver.resolve(query_address, 'TXT')
    ip = resp_two[0].to_text()
    ip = ip.replace('"', '')
    return ip
