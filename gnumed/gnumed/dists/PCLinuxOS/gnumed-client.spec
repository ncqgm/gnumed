#
# spec file for package gnumed-client
#
# Copyright (c) 2007 Sebastian Hilbert, Leipzig, Germany
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.
#
# Please submit bugfixes or comments via http://savannah.gnu.org/bugs/?group=gnumed&func=additem
#

# norootforbuild

%define name    gnumed
%define oname  GNUmed
%define version 0.2.8.3
%define release %mkrel 2

Summary: 	%{oname} client
Name:		%name
Version:		%version
Release:	%release
License:		GPL
Group:		Productivity/Other
Source:		http://www.gnumed.de/downloads/client/0.2/%{oname}-client.%{version}.tgz
Source1:		gnumed-client.conf
Source2:		readme.PCLinuxOS
Patch0:		gnumed-python-path.diff
Patch1:		gnumed.patch
BuildRoot:	%_tmppath/%name-%version-buildroot
URL:		http://wiki.gnumed.de/
Packager:	Gri6507
Distribution:	PCLinuxOS

BuildRequires:	desktop-file-utils

%description
This is the GNUmed Electronic Medical Record. Its purpose is to enable doctors to keep a medically sound record on their patients' health. Currently it is not fully featured. The features provided are, however, tested, in use, and considered stable. This package does NOT yet provide functionality for billing and stock keeping.

While the GNUmed team has taken the utmost care to make sure the medical records are safe at all times you still need to make sure you are taking appropriate steps to backup the medical data to a safe place at appropriate intervals. Do test your backup and desaster recovery procedures, too !

Protect your data! GNUmed itself comes without any warranty whatsoever. You have been warned.

Homepage: http://gnumed.org/

This package contains the wxpython client. 

Authors:
--------
    Sebastian Hilbert <sebastian.hilbert@gmx.net>
    Karsten Hilbert <karsten.hilbert@gmx.net>
    GNUmed team

%package -n %{name}-client
Summary:	Client for %name
Group:		Productivity/Other
Requires:	aspell
Requires:	file
Requires:	gnumed-common = %{version}
Requires:	gnumed-doc = %{version}
Requires:	python >= 2.3
Requires:	libpython2.4-devel
Requires:	python-psycopg2
Requires:	python-mx-base
Requires:	wxPythonGTK
Requires:	kdebase
Requires:	kdepim-korganizer
Requires:	openoffice.org
Requires:	java

%description -n %name-client
The client for %name

%package -n %{name}-common
Summary:	Common files for %name
Group:		Productivity/Other

%description -n %{name}-common
Common files for %name

%package -n %{name}-doc
Summary:	Documentation for %name
Group:		Productivity/Other

%description -n %{name}-doc
Documentation for %name

%prep
%setup -n %{oname}-%{version}
%patch0 -p1
%patch1 -p1

%build

%install

[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf "$RPM_BUILD_ROOT"
mkdir -p "$RPM_BUILD_ROOT"

#python setup.py install --optimize=2 --record-rpm=INSTALLED_FILES \
#      --root="$RPM_BUILD_ROOT"

mkdir -p $RPM_BUILD_ROOT%{_defaultdocdir}/%{name}


mkdir -p $RPM_BUILD_ROOT/etc/gnumed
cp client/connectors/gm_ctl_client.conf $RPM_BUILD_ROOT/etc/gnumed/gm_ctl_client.conf
cp client/doc/gnumed.conf.example $RPM_BUILD_ROOT/etc/gnumed/gnumed.conf
cp %{SOURCE1} $RPM_BUILD_ROOT/etc/gnumed/gnumed-client.conf
cp %{SOURCE2} $RPM_BUILD_ROOT/etc/gnumed/

mkdir -p $RPM_BUILD_ROOT%{_bindir}
cp client/%{name} $RPM_BUILD_ROOT%{_bindir}/%{name}

mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}/bitmaps
cp client/bitmaps/empty-face-in-bust.png $RPM_BUILD_ROOT%{_datadir}/%{name}/bitmaps/empty-face-in-bust.png
cp client/bitmaps/gnumedlogo.png $RPM_BUILD_ROOT%{_datadir}/%{name}/bitmaps/gnumedlogo.png
cp client/bitmaps/serpent.png $RPM_BUILD_ROOT%{_datadir}/%{name}/bitmaps/serpent.png

mkdir -p $RPM_BUILD_ROOT%{_datadir}/locale/fr/LC_MESSAGES/
mkdir -p $RPM_BUILD_ROOT%{_datadir}/locale/de/LC_MESSAGES/
mkdir -p $RPM_BUILD_ROOT%{_datadir}/locale/es/LC_MESSAGES/
cp client/locale/fr-gnumed.mo $RPM_BUILD_ROOT%{_datadir}/locale/fr/LC_MESSAGES/gnumed.mo
cp client/locale/de-gnumed.mo $RPM_BUILD_ROOT%{_datadir}/locale/de/LC_MESSAGES/gnumed.mo
cp client/locale/es-gnumed.mo $RPM_BUILD_ROOT%{_datadir}/locale/es/LC_MESSAGES/gnumed.mo
%find_lang %{name}

mkdir -p $RPM_BUILD_ROOT%{_datadir}/pixmaps
cp client/bitmaps/gnumed.xpm $RPM_BUILD_ROOT%{_datadir}/pixmaps/gnumed.xpm

mkdir -p -m 755  $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/business
cp -r client/business $RPM_BUILD_ROOT%{py_sitedir}/Gnumed

mkdir -p -m755 $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/exporters
cp -r client/exporters $RPM_BUILD_ROOT%{py_sitedir}/Gnumed

mkdir -p -m 755 $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/__init__.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmBorg.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmBusinessDBObject.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmConfigCommon.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmDateTime.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmGuiBroker.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmHooks.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmMatchProvider.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmMimeLib.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmMimeMagic.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmPG2.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmPsql.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmScanBackend.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmScriptingListener.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmShellAPI.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmSignals.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmTools.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon

mkdir -p -m 755 $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/wxGladeWidgets
cp -r client/wxGladeWidgets  $RPM_BUILD_ROOT%{py_sitedir}/Gnumed

mkdir -p -m 755 $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/wxpython/gui
cp -r client/wxpython $RPM_BUILD_ROOT%{py_sitedir}/Gnumed
cp -r client/wxpython/gui $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/wxpython

# TODO: this sed fix should not be here!
%{__sed} -i -e 's@Exec=/usr/bin/gnumed@Exec=/usr/bin/gnumed --conf-file=/etc/%{name}/%{name}-client.conf@' client/%{name}-client.desktop
mkdir -p %buildroot/%{_datadir}/applications/
mkdir -p %buildroot/%{_iconsdir}/
cp client/%{name}-client.desktop $RPM_BUILD_ROOT%{_datadir}/applications/
cp client/bitmaps/%{name}logo.png $RPM_BUILD_ROOT%{_iconsdir}/%{name}.png
desktop-file-install \
    --vendor='' \
    --dir %{buildroot}%{_datadir}/applications \
    --add-category X-MandrivaLinux-Office-Other \
    %{buildroot}%{_datadir}/applications/%{name}-client.desktop

# Files for common package
mkdir -p $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/__init__.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed
cp -r client/pycommon/__init__.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmBackendListener.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmCLI.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmCfg.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmDispatcher.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmExceptions.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmI18N.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmLog.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmLoginInfo.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmNull.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon
cp -r client/pycommon/gmPG.py $RPM_BUILD_ROOT%{py_sitedir}/Gnumed/pycommon

# Files for the doc package
mkdir -p $RPM_BUILD_ROOT%{_defaultdocdir}/%{name}/user-manual
cp -r client/doc/user-manual/* $RPM_BUILD_ROOT%{_defaultdocdir}/%{name}/user-manual


%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf "$RPM_BUILD_ROOT"


%post
%update_menus
# evil hack to get the directory modes straight
chmod 755 /etc/%{name}
chmod -R 755 %{_datadir}/%{name}
chmod -R 755 %{py_sitedir}/Gnumed
chmod 755 %{_bindir}/%{name}


%postun
%clean_menus


%files -n %name-client -f %{name}.lang
%defattr(-,root,root)
%doc %{_defaultdocdir}/%{name}
/etc/%{name}/
%{_bindir}/%name
%{_datadir}/%{name}/bitmaps
%{_datadir}/pixmaps
%{_datadir}/applications/
%{_iconsdir}/
%{py_sitedir}/Gnumed/business/
%{py_sitedir}/Gnumed/exporters/
%{py_sitedir}/Gnumed/wxGladeWidgets/
%{py_sitedir}/Gnumed/wxpython/
%{py_sitedir}/Gnumed/pycommon/__init__.py
%{py_sitedir}/Gnumed/pycommon/gmBorg.py
%{py_sitedir}/Gnumed/pycommon/gmBusinessDBObject.py
%{py_sitedir}/Gnumed/pycommon/gmConfigCommon.py
%{py_sitedir}/Gnumed/pycommon/gmDateTime.py
%{py_sitedir}/Gnumed/pycommon/gmGuiBroker.py
%{py_sitedir}/Gnumed/pycommon/gmHooks.py
%{py_sitedir}/Gnumed/pycommon/gmMatchProvider.py
%{py_sitedir}/Gnumed/pycommon/gmMimeLib.py
%{py_sitedir}/Gnumed/pycommon/gmMimeMagic.py
%{py_sitedir}/Gnumed/pycommon/gmPG2.py
%{py_sitedir}/Gnumed/pycommon/gmPsql.py
%{py_sitedir}/Gnumed/pycommon/gmScanBackend.py
%{py_sitedir}/Gnumed/pycommon/gmScriptingListener.py
%{py_sitedir}/Gnumed/pycommon/gmShellAPI.py
%{py_sitedir}/Gnumed/pycommon/gmSignals.py
%{py_sitedir}/Gnumed/pycommon/gmTools.py

%files -n %name-common
%defattr(-,root,root)
%{py_sitedir}/Gnumed/__init__.py
%{py_sitedir}/Gnumed/pycommon/__init__.py
%{py_sitedir}/Gnumed/pycommon/gmBackendListener.py 
%{py_sitedir}/Gnumed/pycommon/gmCLI.py
%{py_sitedir}/Gnumed/pycommon/gmCfg.py 
%{py_sitedir}/Gnumed/pycommon/gmDispatcher.py 
%{py_sitedir}/Gnumed/pycommon/gmExceptions.py 
%{py_sitedir}/Gnumed/pycommon/gmI18N.py 
%{py_sitedir}/Gnumed/pycommon/gmLog.py 
%{py_sitedir}/Gnumed/pycommon/gmLoginInfo.py 
%{py_sitedir}/Gnumed/pycommon/gmNull.py 
%{py_sitedir}/Gnumed/pycommon/gmPG.py 

%files -n %name-doc
%defattr(-,root,root)
%{_defaultdocdir}/%{name}/user-manual

%changelog
* Fri Feb 1 2008 Paul Grinberg <gri6507 TA yahoo TOD com> - 0.2.8.3-2pclos2007
- Small bug fixes.
- cleaned up requires.

* Thu Jan 31 2008 Paul Grinberg <gri6507 TA yahoo TOD com> - 0.2.8.3-1pclos2007
- Small bug fixes.
- Install the desktop file
- Updated to new version

* Sun Jan 27 2008 Paul Grinberg <gri6507 TA yahoo TOD com> - 0.2.8.2-1pclos2007
- Cleaned up the spec file including combining of the three specs files into one
- Initial publication for PCLinuxOS 2007

* Sun Oct 21 2007 - sebastian.hilbert@gmx.net
- usable version, some weird hacks removed

* Sun Jun 03 2007 - sebastian.hilbert@gmx.net
- Initial creation of package gnumed-client (GNUmed).
