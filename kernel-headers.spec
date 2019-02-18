# For a stable, released kernel, released_kernel should be 1. For rawhide
# and/or a kernel built from an rc or git snapshot, released_kernel should
# be 0.
%global released_kernel 0

# define buildid .local

# baserelease defines which build revision of this kernel version we're
# building.  We used to call this fedora_build, but the magical name
# baserelease is matched by the rpmdev-bumpspec tool, which you should use.
#
# NOTE: baserelease must be > 0 or bad things will happen if you switch
#       to a released kernel (released version will be < rc version)
#
# For non-released -rc kernels, this will be appended after the rcX and
# gitX tags, so a 3 here would become part of release "0.rcX.gitX.3"
#
%global baserelease 1
%global fedora_build %{baserelease}

# base_sublevel is the kernel version we're starting with and patching
# on top of -- for example, 3.1-rc7-git1 starts with a 3.0 base,
# which yields a base_sublevel of 0.
%define base_sublevel 0

## If this is a released kernel ##
%if 0%{?released_kernel}

# Do we have a -stable update to apply?
%define stable_update 0
# Set rpm version accordingly
%if 0%{?stable_update}
%define stablerev %{stable_update}
%define stable_base %{stable_update}
%endif
%define rpmversion 5.%{base_sublevel}.%{stable_update}

## The not-released-kernel case ##
%else
# The next upstream release sublevel (base_sublevel+1)
# %define upstream_sublevel %(echo $((%{base_sublevel} + 1)))
%define upstream_sublevel 0
# The rc snapshot level
%global rcrev 7
# The git snapshot level
%define gitrev 0
# Set rpm version accordingly
%define rpmversion 5.%{upstream_sublevel}.0
%endif

# pkg_release is what we'll fill in for the rpm Release: field
%if 0%{?released_kernel}

%define srcversion %{fedora_build}%{?buildid}

%else

# non-released_kernel
%if 0%{?rcrev}
%define rctag .rc%rcrev
%else
%define rctag .rc0
%endif
%if 0%{?gitrev}
%define gittag .git%gitrev
%else
%define gittag .git0
%endif
%define srcversion 0%{?rctag}%{?gittag}.%{fedora_build}%{?buildid}

%endif

%define pkg_release %{?srcversion}%{?dist}

# This package doesn't contain any binary, thus no debuginfo package is needed
%global debug_package %{nil}

Name: kernel-headers
Summary: Header files for the Linux kernel for use by glibc
License: GPLv2
URL: http://www.kernel.org/
Version: %{rpmversion}
Release: %{pkg_release}
# This is a tarball with headers from the kernel, which should be created
# using create_headers_tarball.sh provided in the kernel source package.
# To create the tarball, you should go into a prepared/patched kernel sources
# directory, or git kernel source repository, and do eg.:
# For a RHEL package: (...)/create_headers_tarball.sh -m RHEL_RELEASE
# For a Fedora package: kernel/scripts/create_headers_tarball.sh -r <release number>
Source0: kernel-headers-%{rpmversion}-%{?srcversion}.tar.xz
Obsoletes: glibc-kernheaders < 3.0-46
Provides: glibc-kernheaders = 3.0-46
%if "0%{?variant}"
Obsoletes: kernel-headers < %{version}-%{release}
Provides: kernel-headers = %{version}-%{release}
%endif

%description
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package -n kernel-cross-headers
Summary: Header files for the Linux kernel for use by cross-glibc

%description -n kernel-cross-headers
Kernel-cross-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
cross-glibc package.

%prep
%setup -q -c

%build

%install
# List of architectures we support and want to copy their headers
ARCH_LIST="arm arm64 powerpc s390 x86"

cd include

ARCH=%_target_cpu
case $ARCH in
	armv7hl)
		ARCH=arm
		;;
	aarch64)
		ARCH=arm64
		;;
	ppc64*)
		ARCH=powerpc
		;;
	s390x)
		ARCH=s390
		;;
	x86_64|i*86)
		ARCH=x86
		;;
esac

mkdir -p $RPM_BUILD_ROOT%{_includedir}
cp -a arch-$ARCH/asm $RPM_BUILD_ROOT%{_includedir}/
cp -a asm-generic $RPM_BUILD_ROOT%{_includedir}

# Copy all the architectures we care about to their respective asm directories
for arch in $ARCH_LIST; do
	mkdir -p $RPM_BUILD_ROOT%{_prefix}/${arch}-linux-gnu/include
	mv arch-${arch}/asm $RPM_BUILD_ROOT%{_prefix}/${arch}-linux-gnu/include/
	cp -a asm-generic $RPM_BUILD_ROOT%{_prefix}/${arch}-linux-gnu/include/
done

# Remove what we copied already
rm -rf arch-*/asm
rmdir arch-*
rm -rf asm-generic

# Copy the rest of the headers over
cp -a * $RPM_BUILD_ROOT%{_includedir}/
for arch in $ARCH_LIST; do
cp -a * $RPM_BUILD_ROOT%{_prefix}/${arch}-linux-gnu/include/
done

%files
%defattr(-,root,root)
%{_includedir}/*

%files -n kernel-cross-headers
%defattr(-,root,root)
%{_prefix}/*-linux-gnu/*

%changelog
* Mon Feb 18 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc7.git0.1
- Linux v5.0-rc7.git0

* Wed Feb 13 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc6.git1.1
- Linux v5.0-rc6.git1

* Mon Feb 11 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc6.git0.1
- Linux v5.0-rc6.git0

* Mon Feb 04 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc5.git0.1
- Linux v5.0-rc5.git0

* Fri Feb 01 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc4.git3.1
- Linux v5.0-rc4.git3

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 5.0.0-0.rc4.git2.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Jan 30 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc4.git2.1
- Linux v5.0-rc4.git2

* Tue Jan 29 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc4.git1.1
- Linux v5.0-rc4.git1

* Mon Jan 28 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc4.git0.1
- Linux v5.0-rc4.git0

* Mon Jan 21 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc3.git0.1
- Linux v5.0-rc3.git0

* Fri Jan 18 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc2.git4.1
- Linux v5.0-rc2.git4

* Thu Jan 17 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc2.git3.1
- Linux v5.0-rc2.git3

* Wed Jan 16 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc2.git2.1
- Linux v5.0-rc2.git2

* Tue Jan 15 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc2.git1.1
- Linux v5.0-rc2.git1

* Mon Jan 14 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc2.git0.1
- Linux v5.0-rc2.git0

* Thu Jan 10 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc1.git3.1
- Linux v5.0-rc1.git3

* Wed Jan 09 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc1.git2.1
- Linux v5.0-rc1.git2

* Tue Jan 08 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc1.git1.1
- Linux v5.0-rc1.git1

* Mon Jan 07 2019 Laura Abbott <labbott@redhat.com> - 5.0.0-0.rc1.git0.1
- Linux v5.0-rc1.git0

* Fri Jan 04 2019 Laura Abbott <labbott@redhat.com> - 4.21.0-0.rc0.git7.1
- Linux v4.21-rc0.git7

* Thu Jan 03 2019 Laura Abbott <labbott@redhat.com> - 4.21.0-0.rc0.git6.1
- Linux v4.21-rc0.git6

* Wed Jan 02 2019 Laura Abbott <labbott@redhat.com> - 4.21.0-0.rc0.git5.1
- Linux v4.21-rc0.git5

* Mon Dec 31 2018 Laura Abbott <labbott@redhat.com> - 4.21.0-0.rc0.git4.1
- Linux v4.21-rc0.git4

* Sun Dec 30 2018 Laura Abbott <labbott@redhat.com> - 4.21.0-0.rc0.git3.1
- Linux v4.21-rc0.git3

* Fri Dec 28 2018 Laura Abbott <labbott@redhat.com> - 4.21.0-0.rc0.git2.1
- Linux v4.21-rc0.git2

* Mon Dec 24 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.21.0-1
- Linux v4.20.0

* Mon Dec 17 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc7.git0.1
- Linux v4.20-rc7.git0

* Mon Dec 10 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc6.git0.1
- Linux v4.20-rc6.git0

* Mon Dec 03 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc5.git0.1
- Linux v4.20-rc5.git0

* Mon Nov 26 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc4.git0.1
- Linux v4.20-rc4.git0

* Tue Nov 20 2018 Jeremy Cline <jcline@redhat.com> - 4.20.0-0.rc3.git1.1
- Linux v4.20-rc3.git1

* Mon Nov 19 2018 Jeremy Cline <jcline@redhat.com> - 4.20.0-0.rc3.git0.1
- Linux v4.20-rc3.git0

* Sun Nov 11 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc2.git0.1
- Linux v4.20-rc2.git0

* Mon Nov 05 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc1.git0.1
- Linux v4.20-rc1.git0

* Fri Nov 02 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git9.1
- Linux v4.20-rc0.git9

* Thu Nov 01 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git8.1
- Linux v4.20-rc0.git8

* Wed Oct 31 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git7.1
- Linux v4.20-rc0.git7

* Tue Oct 30 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git6.1
- Linux v4.20-rc0.git6

* Mon Oct 29 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git5.1
- Linux v4.20-rc0.git5

* Fri Oct 26 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git4.1
- Linux v4.20-rc0.git4

* Thu Oct 25 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git3.1
- Linux v4.20-rc0.git3

* Wed Oct 24 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.20.0-0.rc0.git2.1
- Linux v4.20-rc0.git2

* Tue Oct 23 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.19.0-1
- Linux v4.20-rc0.git1

* Mon Oct 22 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-1
- Linux v4.19.0

* Fri Oct 19 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc8.git4.1
- Linux v4.19-rc8.git4

* Thu Oct 18 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc8.git3.1
- Linux v4.19-rc8.git3

* Wed Oct 17 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc8.git2.1
- Linux v4.19-rc8.git2

* Tue Oct 16 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc8.git1.1
- Linux v4.19-rc8.git1

* Mon Oct 15 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc8.git0.1
- Linux v4.19-rc8.git0

* Fri Oct 12 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc7.git4.1
- Linux v4.19-rc7.git4

* Thu Oct 11 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc7.git3.1
- Linux v4.19-rc7.git3

* Wed Oct 10 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc7.git2.1
- Linux v4.19-rc7.git2

* Tue Oct 09 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc7.git1.1
- Linux v4.19-rc7.git1

* Mon Oct 08 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc7.git0.1
- Linux v4.19-rc7.git0

* Fri Oct 05 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc6.git4.1
- Linux v4.19-rc6.git4

* Thu Oct 04 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc6.git3.1
- Linux v4.19-rc6.git3

* Wed Oct 03 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc6.git2.1
- Linux v4.19-rc6.git2

* Tue Oct 02 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc6.git1.1
- Linux v4.19-rc6.git1

* Mon Oct 01 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc6.git0.1
- Linux v4.19-rc6.git0

* Fri Sep 28 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc5.git3.1
- Linux v4.19-rc5.git3

* Wed Sep 26 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc5.git2.1
- Linux v4.19-rc5.git2

* Tue Sep 25 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc5.git1.1
- Linux v4.19-rc5.git1

* Mon Sep 24 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc5.git0.1
- Linux v4.19-rc5.git0

* Fri Sep 21 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc4.git4.1
- Linux v4.19-rc4.git4

* Thu Sep 20 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc4.git3.1
- Linux v4.19-rc4.git3

* Wed Sep 19 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc4.git2.1
- Linux v4.19-rc4.git2

* Tue Sep 18 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc4.git1.1
- Linux v4.19-rc4.git1

* Mon Sep 17 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc4.git0.1
- Linux v4.19-rc4.git0

* Fri Sep 14 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc3.git3.1
- Linux v4.19-rc3.git3

* Thu Sep 13 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc3.git2.1
- Linux v4.19-rc3.git2

* Wed Sep 12 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc3.git1.1
- Linux v4.19-rc3.git1

* Mon Sep 10 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc3.git0.1
- Linux v4.19-rc3.git0

* Fri Sep 07 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc2.git3.1
- Linux v4.19-rc2.git3

* Thu Sep 06 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc2.git2.1
- Linux v4.19-rc2.git2

* Wed Sep 05 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc2.git1.1
- Linux v4.19-rc2.git1

* Mon Sep 03 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc2.git0.1
- Linux v4.19-rc2.git0

* Fri Aug 31 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc1.git4.1
- Linux v4.19-rc1.git4

* Thu Aug 30 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc1.git3.1
- Linux v4.19-rc1.git3

* Wed Aug 29 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc1.git2.1
- Linux v4.19-rc1.git2

* Tue Aug 28 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc1.git1.1
- Linux v4.19-rc1.git1

* Mon Aug 27 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc1.git0.1
- Linux v4.19-rc1

* Fri Aug 24 2018 Jeremy Cline <jeremy@jcline.org> - 4.19.0-0.rc0.git11.1
- Linux v4.18-12721-g33e17876ea4e

* Thu Aug 23 2018 Jeremy Cline <jeremy@jcline.org> - 4.19.0-0.rc0.git10.1
- Linux v4.18-11682-g815f0ddb346c

* Wed Aug 22 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git9.1
- Linux v4.18-11219-gad1d69735878

* Tue Aug 21 2018 Jeremy Cline <jeremy@jcline.org> - 4.19.0-0.rc0.git8.1
- Linux v4.18-10986-g778a33959a8a

* Mon Aug 20 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git7.1
- Linux v4.18-10721-g2ad0d5269970

* Sun Aug 19 2018 Jeremy Cline <jcline@redhat.com> - 4.19.0-0.rc0.git6.1
- Linux v4.18-10568-g08b5fa819970

* Sat Aug 18 2018 Jeremy Cline <jeremy@jcline.org> - 4.19.0-0.rc0.git5.1
- Linux v4.18-8895-g1f7a4c73a739

* Fri Aug 17 2018 Jeremy Cline <jeremy@jcline.org> - 4.19.0-0.rc0.git4.1
- Linux v4.18-8108-g5c60a7389d79

* Mon Aug 13 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.18.0-1
- Linux v4.18

* Tue Jul 31 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.18.0-0.rc7.git0.1
- Linux v4.18-rc7

* Fri Jul 27 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.18.0-0.rc6.git3.1
- Initial package commit

* Mon Jul 23 2018 Justin M. Forbes <jforbes@fedoraproject.org> - 4.18.0-0.rc6.git0.1
- Changes and updates to fit inline with current Fedora process

* Thu Jul 12 2018 Herton R. Krzesinski <herton@redhat.com> - 4.18.0-0.rc4.2
- Initial version of splitted kernel-headers package.
