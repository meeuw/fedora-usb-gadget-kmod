%global debug_package %{nil}
#rpmbuild --rebuild --define='kernels $(uname -r)' whatever.srpm
#%global buildforkernels akmod
Name: usb-gadget-kmod
Version: 5.19.8
Release: 1%{?dist}
Summary: Akmod package for USB gadget module

License: GPL
URL: http://www.kernel.org
#VERSION=$1
#git clone git://git.kernel.org/pub/scm/linux/kernel/git/stable/linux-stable.git --depth 1 --branch v${VERSION}
#cd linux-stable
#git times # https://git.wiki.kernel.org/index.php/ExampleScripts
#tar cjf linux-drivers-usb-gadget-${VERSION}.tar.xz drivers/usb/gadget/
Source0: linux-drivers-usb-gadget-5.19.8.tar.xz

BuildRequires:  %{_bindir}/kmodtool
Provides: usb-gadget-kmod-common

ExclusiveArch:  i686 x86_64
%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }

# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
Akmod package for USB gadget module

%prep
%{?kmodtool_check}

kmodtool --target %{_target_cpu}  --repo rpmfusion --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

%setup -q -c -T
mkdir %{name}-%{version}-src
pushd %{name}-%{version}-src
tar xf %{SOURCE0}
popd

for kernel_version in %{?kernel_versions} ; do
 cp -a %{name}-%{version}-src _kmod_build_${kernel_version%%___*}
done

%build
for kernel_version in %{?kernel_versions}; do
 pushd _kmod_build_${kernel_version%%___*}/drivers/usb/gadget
 make -C ${kernel_version##*___} M=`pwd` V=1 \
              CONFIG_USB_GADGET=m   CONFIG_USB_DUMMY_HCD=m   CONFIG_USB_LIBCOMPOSITE=m   CONFIG_USB_F_FS=m \
 ccflags-y="-DCONFIG_USB_GADGET=1 -DCONFIG_USB_DUMMY_HCD=1 -DCONFIG_USB_LIBCOMPOSITE=1 -DCONFIG_USB_F_FS=1 -DCONFIG_USB_GADGET_VBUS_DRAW=500 -I`pwd`" \
 modules
 popd
done

%install
rm -rf ${RPM_BUILD_ROOT}
for kernel_version in %{?kernel_versions}; do
 pushd _kmod_build_${kernel_version%%___*}/drivers/usb/gadget
 mkdir -p ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}${kernel_version%%___*}%{kmodinstdir_postfix}
 install -D -m 0755 *.ko -t ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}${kernel_version%%___*}%{kmodinstdir_postfix}
 install -D -m 0755 udc/*.ko -t ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}${kernel_version%%___*}%{kmodinstdir_postfix}udc/
 install -D -m 0755 function/*.ko -t ${RPM_BUILD_ROOT}%{kmodinstdir_prefix}${kernel_version%%___*}%{kmodinstdir_postfix}function/
 popd
done

chmod 0755 $RPM_BUILD_ROOT%{kmodinstdir_prefix}*%{kmodinstdir_postfix}/* || :
%{?akmod_install}

%clean
rm -rf $RPM_BUILD_ROOT

%package -n usb-gadget-kmod-common
Summary: Dummy package

%description  -n usb-gadget-kmod-common
Dummy package

%files -n usb-gadget-kmod-common

%changelog
* Thu Aug  4 2022 Dick Marinus <dick@mrns.nl> - 5.18.15-1
- linux-fs-ntfs-5.18.15
