%global snapshotdate 20160728
%global gitcommit 621f7f3d97400e08ff943cff2d352a174e81dd7e
%global shortcommit %(c=%{gitcommit}; echo ${c:0:7}) 
%global kmod_name rtl8723bs

%{!?kversion: %define kversion 4.4.16-201.el7.centos.%{_target_cpu}}

Name:		kmod-%{kmod_name}
Version:	%{snapshotdate}
Release:	git%{shortcommit}%{?dist}
Summary:    Kernel module for Realtek 8723bs devices

Group:		System Environment/Kernel
License:	GPLv2
URL:		https://github.com/hadess/rtl8723bs
Source0:	rtl8723bs-%{version}-git%{shortcommit}.tar.gz

BuildRequires:	perl
BuildRequires:	redhat-rpm-config
Provides:		kernel-modules = %{kversion}
Provides:		kmod-%{kmod_name} = %{?epoch:%{epoch}:}%{version}-%{release}
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod
Requires:		%{kmod_name}-firmware = %{version}-%{release}

%define debug_package %{nil}

%description
The kernel module to activate the Realtek 8723bs wifi drivers

%package -n %{kmod_name}-firmware
Summary:	Firmware for Realtek 8723bs SDIO devices
BuildArch:  noarch
Requires:	kmod-%{kmod_name} = %{version}-%{release}

%description -n %{kmod_name}-firmware
Firmware for using Realtek 8723bs SDIO Devices

%prep
%setup -q -c -n %{name}-%{version}-%{release}
echo "override rtl8723bs * weak-updates/%{kmod_name}" >> kmod-%{kmod_name}.conf
echo "override rtlwifi * weak-updates/%{kmod_name}" >> kmod-%{kmod_name}.conf

%build
# Remove the checked in files so we can regenerate them
rm -f ./*.bin

%{__cc} -o convert_firmware convert_firmware.c
./convert_firmware

%{__make} modules 
chmod +x r8723bs.ko

%install
%{__install} -d %{buildroot}/lib/modules/%{kversion}/extra/%{kmod_name}/
%{__install} r8723bs.ko %{buildroot}/lib/modules/%{kversion}/extra/%{kmod_name}/rtl8723bs.ko
%{__install} -d %{buildroot}%{_sysconfdir}/depmod.d/
%{__install} kmod-%{kmod_name}.conf %{buildroot}%{_sysconfdir}/depmod.d/

%{__install} -d %{buildroot}/lib/firmware/rtlwifi/
%{__install} rtl8723bs_nic.bin %{buildroot}/lib/firmware/rtlwifi/rtl8723bs_nic.bin
%{__install} rtl8723bs_wowlan.bin %{buildroot}/lib/firmware/rtlwifi/rtl8723bs_wowlan.bin

# strip the modules(s)
find %{buildroot} -type f -name \*.ko -exec %{__strip} --strip-debug \{\} \;

%clean
%{__rm} -rf %{buildroot} 

%post
if [ -e "/boot/System.map-%{kversion}" ]; then
  /usr/sbin/depmod -aeF "/boot/System.map-%{kversion}" "%{kversion}" > /dev/null ||:
fi

%postun
if [ -e "/boot/System.map-%{kversion}" ]; then
  /usr/sbin/depmod -aeF "/boot/System.map-%{kversion}" "%{kversion}" > /dev/null ||:
fi

%files
%defattr(644,root,root,755)
/lib/modules/%{kversion}
%config /etc/depmod.d/kmod-%{kmod_name}.conf

%files -n %{kmod_name}-firmware
%defattr(644,root,root,755)
/lib/firmware/rtlwifi/%{kmod_name}*.bin


%changelog
* Thu Jul 28 2016 brian@bstinson.com - 20160728git621f7f3
- Bump/update for building against the 4.4.16 kernel

* Thu Mar 31 2016 Brian Stinson <brian@bstinson.com> - 20160331git56c76c9
- First build
