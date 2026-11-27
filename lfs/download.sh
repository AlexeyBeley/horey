#!/bin/bash
set -ex

wget https://download.savannah.gnu.org/releases/acl/acl-2.3.2.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 590765dee95907dbc3c856f7255bd669
wget https://download.savannah.gnu.org/releases/attr/attr-2.5.2.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 227043ec2f6ca03c0948df5517f9c927
wget https://ftp.gnu.org/gnu/autoconf/autoconf-2.72.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 1be79f7106ab6767f18391c5e22be701
wget https://ftp.gnu.org/gnu/automake/automake-1.17.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 7ab3a02318fee6f5bd42adfc369abf10
wget https://ftp.gnu.org/gnu/bash/bash-5.2.32.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: f204835b2e06c06e37b5ad776ff907f4
wget https://github.com/gavinhoward/bc/releases/download/6.7.6/bc-6.7.6.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: a47aa5e4e7395fbcd159a9228613b97b
wget https://sourceware.org/pub/binutils/releases/binutils-2.43.1.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 9202d02925c30969d1917e4bad5a2320
wget https://ftp.gnu.org/gnu/bison/bison-3.8.2.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: c28f119f405a2304ff0a7ccdcc629713
wget https://www.sourceware.org/pub/bzip2/bzip2-1.0.8.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 67e051268d0c475ea773822f7500d0e5
wget https://github.com/libcheck/check/releases/download/0.15.2/check-0.15.2.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 50fcafcecde5a380415b12e9c574e0b2
wget https://ftp.gnu.org/gnu/coreutils/coreutils-9.5.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: e99adfa059a63db3503cc71f3d151e31
wget https://ftp.gnu.org/gnu/dejagnu/dejagnu-1.6.3.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 68c5208c58236eba447d7d6d1326b821
wget https://ftp.gnu.org/gnu/diffutils/diffutils-3.10.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 2745c50f6f4e395e7b7d52f902d075bf
wget https://downloads.sourceforge.net/project/e2fsprogs/e2fsprogs/v1.47.1/e2fsprogs-1.47.1.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 75e6d1353cbe6d5728a98fb0267206cb
wget https://sourceware.org/ftp/elfutils/0.191/elfutils-0.191.tar.bz2 --directory-prefix=$LFS/sources
# MD5 sum: 636547248fb3fae58ec48030298d3ef7

todo:
wget https://prdownloads.sourceforge.net/expat/expat-2.6.2.tar.xz --directory-prefix=$LFS/sources

# MD5 sum: 0cb75c8feb842c0794ba89666b762a2d
wget https://prdownloads.sourceforge.net/expect/expect5.45.4.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 00fce8de158422f5ccd2666512329bd2
wget https://astron.com/pub/file/file-5.45.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 26b2a96d4e3a8938827a1e572afd527a
wget https://ftp.gnu.org/gnu/findutils/findutils-4.10.0.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 870cfd71c07d37ebe56f9f4aaf4ad872
wget https://github.com/westes/flex/releases/download/v2.6.4/flex-2.6.4.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 2882e3179748cc9f9c23ec593d6adc8d
wget https://pypi.org/packages/source/f/flit-core/flit_core-3.9.0.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 3bc52f1952b9a78361114147da63c35b
wget https://ftp.gnu.org/gnu/gawk/gawk-5.3.0.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 97c5a7d83f91a7e1b2035ebbe6ac7abd
wget https://ftp.gnu.org/gnu/gcc/gcc-14.2.0/gcc-14.2.0.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 2268420ba02dc01821960e274711bde0
wget https://ftp.gnu.org/gnu/gdbm/gdbm-1.24.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: c780815649e52317be48331c1773e987
wget https://ftp.gnu.org/gnu/gettext/gettext-0.22.5.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 3ae5580599d84be93e6213930facb2db
wget https://ftp.gnu.org/gnu/glibc/glibc-2.40.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: b390feef233022114950317f10c4fa97
wget https://ftp.gnu.org/gnu/gmp/gmp-6.3.0.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 956dc04e864001a9c22429f761f2c283
wget https://ftp.gnu.org/gnu/gperf/gperf-3.1.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 9e251c0a618ad0824b51117d5d9db87e
wget https://ftp.gnu.org/gnu/grep/grep-3.11.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 7c9bbd74492131245f7cdb291fa142c0
wget https://ftp.gnu.org/gnu/groff/groff-1.23.0.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 5e4f40315a22bb8a158748e7d5094c7d
wget https://ftp.gnu.org/gnu/grub/grub-2.12.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 60c564b1bdc39d8e43b3aab4bc0fb140
wget https://ftp.gnu.org/gnu/gzip/gzip-1.13.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: d5c9fc9441288817a4a0be2da0249e29
wget https://github.com/Mic92/iana-etc/releases/download/20240806/iana-etc-20240806.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: ea3c37c00d22f1159fc3b7d988de8476
wget https://ftp.gnu.org/gnu/inetutils/inetutils-2.5.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 9e5a6dfd2d794dc056a770e8ad4a9263
wget https://launchpad.net/intltool/trunk/0.51.0/+download/intltool-0.51.0.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 12e517cac2b57a0121cda351570f1e63
wget https://www.kernel.org/pub/linux/utils/net/iproute2/iproute2-6.10.0.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 6282e47de9c5b230e83537fba7181c9c
wget https://pypi.org/packages/source/J/Jinja2/jinja2-3.1.4.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 02ca9a6364c92e83d14b037bef4732bc
wget https://www.kernel.org/pub/linux/utils/kbd/kbd-2.6.4.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: e2fd7adccf6b1e98eb1ae8d5a1ce5762
wget https://www.kernel.org/pub/linux/utils/kernel/kmod/kmod-33.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: c451c4aa61521adbe8af147f498046f8
wget https://www.greenwoodsoftware.com/less/less-661.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 44f54b6313c5d71fa1ac224d8d84766a
wget https://www.linuxfromscratch.org/lfs/downloads/12.2/lfs-bootscripts-20240825.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 4dd8a52530eec8f8a544f833e2a82eaf
wget https://www.kernel.org/pub/linux/libs/security/linux-privs/libcap2/libcap-2.70.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: df0e20c6eeca849347b87d5d6a8870c0
wget https://github.com/libffi/libffi/releases/download/v3.4.6/libffi-3.4.6.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: b9cac6c5997dca2b3787a59ede34e0eb
wget https://download.savannah.gnu.org/releases/libpipeline/libpipeline-1.5.7.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 1a48b5771b9f6c790fb4efdb1ac71342
wget https://ftp.gnu.org/gnu/libtool/libtool-2.4.7.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 2fc0b6ddcd66a89ed6e45db28fa44232
wget https://github.com/besser82/libxcrypt/releases/download/v4.4.36/libxcrypt-4.4.36.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: b84cd4104e08c975063ec6c4d0372446
wget https://www.kernel.org/pub/linux/kernel/v6.x/linux-6.10.5.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 276ef1f11ed3713ec5d6f506ff55ac12
wget https://github.com/lz4/lz4/releases/download/v1.10.0/lz4-1.10.0.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: dead9f5f1966d9ae56e1e32761e4e675
wget https://ftp.gnu.org/gnu/m4/m4-1.4.19.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 0d90823e1426f1da2fd872df0311298d
wget https://ftp.gnu.org/gnu/make/make-4.4.1.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: c8469a3713cbbe04d955d4ae4be23eeb
wget https://download.savannah.gnu.org/releases/man-db/man-db-2.12.1.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 7b044e5020aab89db41ac7ee59d6d84a
wget https://www.kernel.org/pub/linux/docs/man-pages/man-pages-6.9.1.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 4d56775b6cce4edf1e496249e7c01c1a
wget https://pypi.org/packages/source/M/MarkupSafe/MarkupSafe-2.1.5.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 8fe7227653f2fb9b1ffe7f9f2058998a
wget https://github.com/mesonbuild/meson/releases/download/1.5.1/meson-1.5.1.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: c4f2b3e5ea632685f61ba1b833c4905c
wget https://ftp.gnu.org/gnu/mpc/mpc-1.3.1.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 5c9bc658c9fd0f940e8e3e0f09530c62
wget https://ftp.gnu.org/gnu/mpfr/mpfr-4.2.1.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 523c50c6318dde6f9dc523bc0244690a
wget https://invisible-mirror.net/archives/ncurses/ncurses-6.5.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: ac2d2629296f04c8537ca706b6977687
wget https://github.com/ninja-build/ninja/archive/v1.12.1/ninja-1.12.1.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 6288992b05e593a391599692e2f7e490
wget https://www.openssl.org/source/openssl-3.3.1.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 8a4342b399c18f870ca6186299195984
wget https://ftp.gnu.org/gnu/patch/patch-2.7.6.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 78ad9937e4caadcba1526ef1853730d5
wget https://www.cpan.org/src/5.0/perl-5.40.0.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: cfe14ef0709b9687f9c514042e8e1e82
wget https://distfiles.ariadne.space/pkgconf/pkgconf-2.3.0.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 833363e77b5bed0131c7bc4cc6f7747b
wget https://sourceforge.net/projects/procps-ng/files/Production/procps-ng-4.0.4.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 2f747fc7df8ccf402d03e375c565cf96
wget https://sourceforge.net/projects/psmisc/files/psmisc/psmisc-23.7.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 53eae841735189a896d614cba440eb10
wget https://www.python.org/ftp/python/3.12.5/Python-3.12.5.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 02c7d269e077f4034963bba6befdc715
wget https://www.python.org/ftp/python/doc/3.12.5/python-3.12.5-docs-html.tar.bz2 --directory-prefix=$LFS/sources
# MD5 sum: 52274d813236ca4a972fb6988480dc56
wget https://ftp.gnu.org/gnu/readline/readline-8.2.13.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 05080bf3801e6874bb115cd6700b708f
wget https://ftp.gnu.org/gnu/sed/sed-4.9.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 6aac9b2dbafcd5b7a67a8a9bcb8036c3
wget https://pypi.org/packages/source/s/setuptools/setuptools-72.2.0.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 2e0ffd0f6fc632a11442b79d9b1c68bd
wget https://github.com/shadow-maint/shadow/releases/download/4.16.0/shadow-4.16.0.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: eb70bad3316d08f0d3bb3d4bbeccb3b4
wget https://github.com/troglobit/sysklogd/releases/download/v2.6.1/sysklogd-2.6.1.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: dcf0836a0fcc6568efaad230850d9c86
wget https://github.com/systemd/systemd/archive/v256.4/systemd-256.4.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 03bd1ff158ec0bc55428c77a8f8495bd
wget https://anduin.linuxfromscratch.org/LFS/systemd-man-pages-256.4.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 8dbcf0ff0d8e5e9d3565f9d2fc153310
wget https://github.com/slicer69/sysvinit/releases/download/3.10/sysvinit-3.10.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: b8fbe11062cf16d3b6a3709b7f6978d2
wget https://ftp.gnu.org/gnu/tar/tar-1.35.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: a2d8042658cfd8ea939e6d911eaf4152
wget https://downloads.sourceforge.net/tcl/tcl8.6.14-src.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: c30b57c6051be28fa928d09aca82841e
wget https://downloads.sourceforge.net/tcl/tcl8.6.14-html.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 5467198f8d57c54835bf80b98ffb0170
wget https://ftp.gnu.org/gnu/texinfo/texinfo-7.1.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: edd9928b4a3f82674bcc3551616eef3b
wget https://www.iana.org/time-zones/repository/releases/tzdata2024a.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 2349edd8335245525cc082f2755d5bf4
wget https://anduin.linuxfromscratch.org/LFS/udev-lfs-20230818.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: acd4360d8a5c3ef320b9db88d275dae6
wget https://www.kernel.org/pub/linux/utils/util-linux/v2.40/util-linux-2.40.2.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: 88faefc8fefced097e58142077a3d14e
wget https://github.com/vim/vim/archive/v9.1.0660/vim-9.1.0660.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: c512a99b3704f193be1a181cc644b2b2
wget https://pypi.org/packages/source/w/wheel/wheel-0.44.0.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 440ff4fe51579b7ed16f02af8f8d9494
wget https://cpan.metacpan.org/authors/id/T/TO/TODDR/XML-Parser-2.47.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 89a8e82cfd2ad948b349c0a69c494463
wget https://github.com//tukaani-project/xz/releases/download/v5.6.2/xz-5.6.2.tar.xz --directory-prefix=$LFS/sources
# MD5 sum: bbf73fb28425cebb854328599f85c4cf
wget https://zlib.net/fossils/zlib-1.3.1.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 9855b6d802d7fe5b7bd5b196a2271655
wget https://github.com/facebook/zstd/releases/download/v1.5.6/zstd-1.5.6.tar.gz --directory-prefix=$LFS/sources
# MD5 sum: 5a473726b3445d0e5d6296afd1ab6854
wget https://www.linuxfromscratch.org/patches/lfs/12.2/bzip2-1.0.8-install_docs-1.patch --directory-prefix=$LFS/sources
# MD5 sum: 6a5ac7e89b791aae556de0f745916f7f
wget https://www.linuxfromscratch.org/patches/lfs/12.2/coreutils-9.5-i18n-2.patch --directory-prefix=$LFS/sources
# MD5 sum: 58961caf5bbdb02462591fa506c73b6d
wget https://www.linuxfromscratch.org/patches/lfs/12.2/expect-5.45.4-gcc14-1.patch --directory-prefix=$LFS/sources
# MD5 sum: 0b8b5ac411d011263ad40b0664c669f0
wget https://www.linuxfromscratch.org/patches/lfs/12.2/glibc-2.40-fhs-1.patch --directory-prefix=$LFS/sources
# MD5 sum: 9a5997c3452909b1769918c759eff8a2
wget https://www.linuxfromscratch.org/patches/lfs/12.2/kbd-2.6.4-backspace-1.patch --directory-prefix=$LFS/sources
# MD5 sum: f75cca16a38da6caa7d52151f7136895
wget https://www.linuxfromscratch.org/patches/lfs/12.2/sysvinit-3.10-consolidated-1.patch --directory-prefix=$LFS/sources
# MD5 sum: 17ffccbb8e18c39e8cedc32046f3a475