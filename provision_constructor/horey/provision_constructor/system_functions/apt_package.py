import pdb
from horey.h_logger import get_logger

logger = get_logger()


class APTPackage:
    def __init__(self):
        self.name = None
        self.package_list_names = None
        self.str_src = None

    def init_from_line(self, str_src):
        """
        ['accountsservice/focal-updates', 'focal-security', 'now 0.6.55-0ubuntu12~20.04.5 amd64 [installed', 'automatic]']

        Package: accountsservice
        Version: 0.6.55-0ubuntu12~20.04.5
        Priority: standard
        Section: gnome
        Origin: Ubuntu
        Maintainer: Ubuntu Developers <ubuntu-devel-discuss@lists.ubuntu.com>
        Original-Maintainer: Debian freedesktop.org maintainers <pkg-freedesktop-maintainers@lists.alioth.debian.org>
        Bugs: https://bugs.launchpad.net/ubuntu/+filebug
        Installed-Size: 463 kB
        Depends: dbus, libaccountsservice0 (= 0.6.55-0ubuntu12~20.04.5), libc6 (>= 2.4), libglib2.0-0 (>= 2.44), libpolkit-gobject-1-0 (>= 0.99)
        Suggests: gnome-control-center
        Homepage: https://www.freedesktop.org/wiki/Software/AccountsService/
        Task: standard
        Download-Size: 61.0 kB
        APT-Manual-Installed: no
        APT-Sources: http://us-east-1.ec2.archive.ubuntu.com/ubuntu focal-updates/main amd64 Packages
        Description: query and manipulate user account information
         The AccountService project provides a set of D-Bus
         interfaces for querying and manipulating user account
         information and an implementation of these interfaces,
         based on the useradd, usermod and userdel commands.

        @param str_src:
        @return:
        """
        self.str_src = str_src

        first_octet = str_src.split(" ")[0]

        self.name, self.package_list_names = first_octet.split("/")
