"""
Access to docker Registry
"""

import requests

MANIFEST_TYPES = ",".join([
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
])


class Registry:
    """
    Access to docker Registry
    """
    def __init__(self, host, user=None, password=None, basic_auth=False):
        self.host = host
        self.base = f"https://{host}"
        self.auth = (user, password) if user else None
        self.tokens = {}          # scope -> bearer token
        self.session = requests.Session()
        self.basic_auth = basic_auth

    def _bearer(self, challenge, scope):
        """
        Fetch bearer token per scope.

        """

        # challenge: Bearer realm="...",service="...",scope="..."
        parts = dict(p.split("=", 1) for p in challenge[len("Bearer "):].split(","))
        parts = {k.strip(): v.strip('"') for k, v in parts.items()}
        r = requests.get(
            parts["realm"],
            params={"service": parts.get("service", ""), "scope": scope},
            auth=self.auth,
        )
        r.raise_for_status()
        j = r.json()
        return j.get("token") or j.get("access_token")

    def request(self, method, path, scope, **kw):
        """
        Perform the request
        """
        url = path if path.startswith("http") else self.base + path
        headers = kw.pop("headers", {}).copy()
        kw.setdefault("timeout", (10, 300))

        if scope in self.tokens:
            headers["Authorization"] = f"Bearer {self.tokens[scope]}"
        elif self.basic_auth:
            kw["auth"] = self.auth                   # preemptive Basic

        # pylint: disable = missing-timeout
        ret = self.session.request(method, url, headers=headers, **kw)
        if ret.status_code != 401:
            return ret

        if kw.get("data") is not None and hasattr(kw["data"], "read"):
            raise RuntimeError(f"401 on streamed upload to {url}; auth must be primed first")

        ch = ret.headers.get("WWW-Authenticate", "")
        if ch.startswith("Bearer "):
            self.tokens[scope] = self._bearer(ch, scope)
            headers["Authorization"] = f"Bearer {self.tokens[scope]}"
        elif ch.startswith("Basic") and self.auth:
            kw["auth"] = self.auth
        else:
            ret.raise_for_status()
        
        # note: a streamed body can't be replayed; blob uploads are
        # preceded by a POST/HEAD that primes the token, so this is fine
        
        # pylint: disable = missing-timeout
        return self.session.request(method, url, headers=headers, **kw)

    def blob_exists(self, repo:str, digest:str):
        """
        Check if blob exists.
        """

        ret = self.request("HEAD", f"/v2/{repo}/blobs/{digest}", f"repository:{repo}:pull,push")
        return ret.status_code == 200
