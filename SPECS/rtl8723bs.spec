%global snapshotdate 20160331
%global gitcommit 56c76c958de0521238d75fc789b2dd7363257458
%global shortcommit %(c=%{gitcommit}; echo ${c:0:7}) 
%global kmod_name rtl8723bs

%{!?kversion: %define kversion 4.4.6-301.el7.%{_target_cpu}}

Name:		%{kmod_name}-kmod
Version:	%{snapshotdate}
Release:	%{shortcommit}%{?dist}
Summary:    Kernel module for Realtek 8723bs devices

Group:		System Environment/Kernel
License:	GPLv2
URL:		https://github.com/hadess/rtl8723bs
Source0:	rtl8723bs-%{version}-git%{shortcommit}.tar.gz
Source1:    kmodtool-%{kmod_name}.sh

BuildRequires:	perl
BuildRequires:	redhat-rpm-config

%{expand:%(sh %{SOURCE1} rpmtemplate %{kmod_name} %{kversion} "")}
%define debug_package %{nil}

%description
The kernel module to activate the Realtek 8723bs wifi drivers

%package -n %{kmod_name}-firmware
Summary:	Firmware for Realtek 8723bs SDIO devices
BuildArch:  noarch

%description -n %{kmod_name}-firmware
Firmware for using Realtek 8723bs SDIO Devices

%prep
%setup -q -c -n %{name}-%{version}-%{release}
echo "override r8723bs * weak-updates/%{kmod_name}" >> kmod-%{kmod_name}.conf

%build
# Remove the checked in files so we can regenerate them
rm -f ./*.bin

%{__cc} -o convert_firmware convert_firmware.c
./convert_firmware

%{__make} modules 
chmod +x r8723bs.ko

%install
%{__install} -d %{buildroot}/lib/modules/%{kversion}/kernel/drivers/net/wireless/
%{__install} r8723bs.ko %{buildroot}/lib/modules/%{kversion}/kernel/drivers/net/wireless/
%{__install} -d %{buildroot}%{_sysconfdir}/depmod.d/
%{__install} kmod-%{kmod_name}.conf %{buildroot}%{_sysconfdir}/depmod.d/

%{__install} -d %{buildroot}/lib/firmware/rtlwifi/
%{__install} rtl8723bs_nic.bin %{buildroot}/lib/firmware/rtlwifi/rtl8723bs_nic.bin
%{__install} rtl8723bs_wowlan.bin %{buildroot}/lib/firmware/rtlwifi/rtl8723bs_wowlan.bin

# strip the modules(s)
find %{buildroot} -type f -name \*.ko -exec %{__strip} --strip-debug \{\} \;

%clean
%{__rm} -rf %{buildroot} 

%files
/etc/depmod.d/kmod-%{kmod_name}.conf

%files -n %{kmod_name}-firmware
/lib/firmware/rtlwifi/%{kmod_name}*.bin

%changelog
* Thu Mar 31 2016 Brian Stinson <brian@bstinson.com> - 20160331git56c76c9
- First build
