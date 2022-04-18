%define _binaries_in_noarch_packages_terminate_build 0

Name:           syslinux
Version:        6.04
Release:        11
License:        GPLv2+
Summary:        The Syslinux boot loader collection
URL:            http://syslinux.zytor.com/wiki/index.php/The_Syslinux_Project
Source0:        https://mirrors.edge.kernel.org/pub/linux/utils/boot/syslinux/Testing/6.04/syslinux-6.04-pre1.tar.xz
ExclusiveArch:  x86_64
BuildRequires:  nasm >= 0.98.38-1 perl-interpreter libuuid-devel gcc
Requires:       syslinux-nonlinux = %{version}-%{release} mtools

# Add install all target in top Makefile.
# From: https://raw.githubusercontent.com/OpenMandrivaAssociation/syslinux/master/0001-Add-install-all-target-to-top-side-of-HAVE_FIRMWARE.patch
Patch0001:      0001-Add-install-all-target-to-top-side-of-HAVE_FIRMWARE.patch

# Enable ext4 64bit feature.
# From: https://raw.githubusercontent.com/JeffreyALaw/Fedora-syslinux/master/0002-ext4-64bit-feature.patch
Patch0002:      0002-ext4-64bit-feature.patch

# Add include sysmacros.h to fixed building error.
# Frome: https://raw.githubusercontent.com/JeffreyALaw/Fedora-syslinux/master/0003-include-sysmacros-h.patch
Patch0003:      0003-include-sysmacros-h.patch

Patch0004:      backport-replace-builtin-strlen-that-appears-to-get-optimized.patch
Patch0005:      backport-add-RPMOPTFLAGS-to-CFLAGS-for-some-stuff.patch
Patch0006:      backport-tweak-for-gcc-10.patch

%description
The Syslinux Project covers lightweight bootloaders for MS-DOS FAT filesystems (SYSLINUX),
network booting (PXELINUX), bootable "El Torito" CD-ROMs (ISOLINUX), and Linux ext2/ext3/ext4
or btrfs filesystems (EXTLINUX). The project also includes MEMDISK, a tool to boot legacy
operating systems (such as DOS) from nontraditional media; it is usually used in conjunction
with PXELINUX and ISOLINUX.

%package        perl
Summary:        Tools for using syslinux

%description    perl
Tools for using syslinux.

%package        devel
Summary:        Documentation for developing syslinux
Provides:       syslinux-static = %{version}-%{release}

%description    devel
Documentation for developing syslinux.

%package        extlinux
Summary:        Modules for booting the local system
Requires:       syslinux syslinux-extlinux-nonlinux = %{version}-%{release}

%description    extlinux
Modules for booting the local system

%package        tftpboot
Summary:        Modules for network booting
BuildArch:      noarch
ExclusiveArch:  x86_64
Requires:       syslinux

%description    tftpboot
Modules for network booting

%package        extlinux-nonlinux
Summary:        extlinux modules which aren't run from linux
BuildArch:      noarch
ExclusiveArch:  x86_64
Requires:       syslinux

%description    extlinux-nonlinux
extlinux modules which aren't run from linux.

%package        nonlinux
Summary:        syslinux modules which aren't run from linux
BuildArch:      noarch
ExclusiveArch:  x86_64
Requires:       syslinux

%description    nonlinux
syslinux modules which aren't run from linux.

%package        efi64
Summary:        Modules for 64-bit UEFI systems

%description    efi64
Modules for 64-bit UEFI systems.

%prep
%autosetup -n syslinux-6.04-pre1 -p1

%build
make RPMCFLAGS='%{optflags}' RPMLDFLAGS='%{build_ldflags}' bios clean all
make RPMCFLAGS='%{optflags}' RPMLDFLAGS='%{build_ldflags}' efi64 clean all

%install
rm -rf %{buildroot}
install -d %{buildroot}%{_bindir}
install -d %{buildroot}/sbin
install -d %{buildroot}%{_prefix}/lib/syslinux
install -d %{buildroot}%{_includedir}
make bios install-all INSTALLROOT=%{buildroot} BINDIR=%{_bindir} SBINDIR=/sbin \
  LIBDIR=%{_prefix}/lib DATADIR=%{_datadir} MANDIR=%{_mandir} INCDIR=%{_includedir} \
  TFTPBOOT=/tftpboot EXTLINUXDIR=/boot/extlinux LDLINUX=ldlinux.c32
make efi64 install netinstall INSTALLROOT=%{buildroot} BINDIR=%{_bindir} SBINDIR=/sbin \
  LIBDIR=%{_prefix}/lib DATADIR=%{_datadir} MANDIR=%{_mandir} INCDIR=%{_includedir} \
  TFTPBOOT=/tftpboot EXTLINUXDIR=/boot/extlinux LDLINUX=ldlinux.c32
install -d %{buildroot}%{_pkgdocdir}/sample
install -m 644 sample/sample.* %{buildroot}%{_pkgdocdir}/sample/
install -d %{buildroot}/etc
( cd %{buildroot}/etc && ln -s ../boot/extlinux/extlinux.conf . )

%post extlinux
if [ -f /boot/extlinux/extlinux.conf ]; then
  extlinux --update /boot/extlinux
elif [ -f /boot/extlinux.conf ]; then
  mkdir -p /boot/extlinux && mv /boot/extlinux.conf /boot/extlinux/extlinux.conf && extlinux --update /boot/extlinux
fi

%files
%doc COPYING NEWS README*
%doc doc/* sample
%{_mandir}/man1/{gethostip*,syslinux*,extlinux*,isohybrid*,memdiskfind*}
%{_datadir}/doc/syslinux/sample/sample.msg 
%{_bindir}/{gethostip,isohybrid,memdiskfind,syslinux}
%dir %{_datadir}/syslinux/dosutil
%{_datadir}/syslinux/dosutil/*
%dir %{_datadir}/syslinux/diag
%{_datadir}/syslinux/{diag/*,syslinux64.exe}
%exclude %{_prefix}/lib/libsyslinux*
%exclude %{_includedir}/syslinux.h

%files perl
%doc COPYING
%{_mandir}/man1/{lss16toppm*,ppmtolss16*,syslinux2ansi*}
%{_bindir}/{keytab-lilo,lss16toppm,md5pass,mkdiskimage,ppmtolss16,pxelinux-options,sha1pass,syslinux2ansi,isohybrid.pl}

%files devel
%doc COPYING
%dir %{_datadir}/syslinux/com32
%{_datadir}/syslinux/com32/*

%files extlinux
/sbin/extlinux
%config /etc/extlinux.conf

%files tftpboot
/tftpboot

%files nonlinux
%{_datadir}/syslinux/{memdisk,*.com,*.exe,*.c32,*.bin,*.0}

%files extlinux-nonlinux
/boot/extlinux

%files efi64
%doc COPYING
%dir %{_datadir}/syslinux/efi64
%{_datadir}/syslinux/efi64

%changelog
* Mon Aug 23 2021 yangcheng<yangcheng87@huawei.com> - 6.04-11
- Increase perl and gcc dependencies in buildrequires

* Thu Aug 12 2021 yangcheng<yangcheng87@huawei.com> - 6.04-10
- streamline the build dependency and fix the compiling stuck

* Fri Jul 30 2021 hanhui<hanhui15@huawei.com> - 6.04-9
- fix build failed due to gcc-10

* Fri Jul 16 2021 hanhui<hanhui15@huawei.com> - 6.04-8
- solves the problem of compiling stuck

* Sat Mar 20 2021 hanhui<hanhui15@huawei.com> - 6.04-7
- slove the problem of security scanning of options

* Sun Feb 7 2021 jinzhimin<jinzhimin2@huawei.com> - 6.04-6
- add patch to replace builtin strlen

* Mon Mar 2 2020 songnannan<songnannan2@huawei.com> -6.04-5
- change the path of file

* Mon Mar 2 2020 songnannan<songnannan2@huawei.com> - 6.04-4 
- change files

* Mon Mar 2 2020 songnannan<songnannan2@huawei.com> - 6.04-3
- add sample.msg file to help package

* Mon Mar 2 2020 songnannan<songnannan2@huawei.com> - 6.04-2
- change the mingw64-gcc to gcc in buildrequires

* Thu Feb 27 2020 Ling Yang <lingyang2@huawei.com> - 6.04-1
- Package Init
