#
# spec file for package gnumed-client (Version 0.2.7.1)
#
# Copyright (c) 2007 Sebastian Hilbert, Leipzig, Germany
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.
#
# Please submit bugfixes or comments via http://savannah.gnu.org/bugs/?group=gnumed&func=additem
#

# norootforbuild

Name:           gnumed-client
Summary:        An electronic medical record and patient record archive
License:        GPL
Version:        0.2.7.1
Release:        0.0
Group:          Productivity/Publishing/Other
Source:         http://www.gnumed.de/downloads/client/0.2/GNUmed-client.%{version}.tgz
Patch0:         gnumed-python-path.diff
#Patch1:         
#Patch2:         
Requires:  	aspell file gnumed-common = %{version} gnumed-doc = %{version} python >= 2.3 python-devel python-psycopg2 python-egenix-mx-base python-wxGTK > 2.6.3
# suggested MozillaFirefox libextractor xntp xmedcon xsane python-enchant
PreReq:         filesystem /usr/bin/touch
Provides:       gnumed-client
#Obsoletes:     
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
URL:            http://wiki.gnumed.de/

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


%debug_package

%prep
%setup -n GNUmed-%{version}
%patch -p1

#%build

%install

[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf "$RPM_BUILD_ROOT"
mkdir -p "$RPM_BUILD_ROOT"

#python setup.py install --optimize=2 --record-rpm=INSTALLED_FILES \
#      --root="$RPM_BUILD_ROOT"

mkdir -p $RPM_BUILD_ROOT%{_defaultdocdir}/%{name}


mkdir -p $RPM_BUILD_ROOT/etc/gnumed
cp client/connectors/gm_ctl_client.conf $RPM_BUILD_ROOT/etc/gnumed/gm_ctl_client.conf
cp client/doc/gnumed.conf.example $RPM_BUILD_ROOT/etc/gnumed/gnumed.conf
cp client/doc/gnumed.conf.example $RPM_BUILD_ROOT/etc/gnumed/gnumed-client.conf

#cp gnumed/usr/bin/gm_ctl_client /usr/bin/gm_ctl_client
mkdir -p $RPM_BUILD_ROOT/usr/bin
cp client/gnumed $RPM_BUILD_ROOT/usr/bin/gnumed
    
#/usr/share/applications/gnumed-client.desktop
#/usr/share/doc/gnumed-client/README.Debian
#/usr/share/doc/gnumed-client/changelog.Debian.gz
#/usr/share/doc/gnumed-client/copyright

mkdir -p $RPM_BUILD_ROOT/usr/share/gnumed/bitmaps
cp client/bitmaps/empty-face-in-bust.png $RPM_BUILD_ROOT/usr/share/gnumed/bitmaps/empty-face-in-bust.png
cp client/bitmaps/gnumedlogo.png $RPM_BUILD_ROOT/usr/share/gnumed/bitmaps/gnumedlogo.png
cp client/bitmaps/serpent.png $RPM_BUILD_ROOT/usr/share/gnumed/bitmaps/serpent.png

mkdir -p $RPM_BUILD_ROOT/usr/share/locale/de/LC_MESSAGES
cp client/locale/de-gnumed.mo $RPM_BUILD_ROOT/usr/share/locale/de/LC_MESSAGES/gnumed.mo
mkdir -p $RPM_BUILD_ROOT/usr/share/locale/es/LC_MESSAGES
cp client/locale/es-gnumed.mo $RPM_BUILD_ROOT/usr/share/locale/es/LC_MESSAGES/gnumed.mo
mkdir -p $RPM_BUILD_ROOT/usr/share/locale/fr/LC_MESSAGES
cp client/locale/fr-gnumed.mo $RPM_BUILD_ROOT/usr/share/locale/fr/LC_MESSAGES/gnumed.mo

mkdir -p $RPM_BUILD_ROOT/usr/share/pixmaps
cp client/bitmaps/gnumed.xpm $RPM_BUILD_ROOT/usr/share/pixmaps/gnumed.xpm

mkdir -p -m 755  $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/business
cp -r client/business $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed

mkdir -p -m755 $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/exporters
cp -r client/exporters $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed

mkdir -p -m 755 $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/__init__.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmBorg.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmBusinessDBObject.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmConfigCommon.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmDateTime.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmGuiBroker.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmHooks.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmMatchProvider.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmMimeLib.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmMimeMagic.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmPG2.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmPsql.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmScanBackend.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmScriptingListener.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmShellAPI.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmSignals.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon
cp -r client/pycommon/gmTools.py $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/pycommon

mkdir -p -m 755 $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/wxGladeWidgets
cp -r client/wxGladeWidgets  $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed

mkdir -p -m 755 $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/wxpython/gui
cp -r client/wxpython $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed
cp -r client/wxpython/gui $RPM_BUILD_ROOT/usr/lib/python/site-packages/Gnumed/wxpython

find -P $RPM_BUILD_ROOT -type f | sed s#$RPM_BUILD_ROOT##g > INSTALLED_FILES 

#cp -p COPYING INSTALL PKG-INFO TODO README $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}/
#cp -pr examples doc  $RPM_BUILD_ROOT/%{_defaultdocdir}/%{name}/

#/usr/share/man/man1/gm_ctl_client.1.gz
#/usr/share/man/man1/gnumed.1.gz
#/usr/share/menu/gnumed-client

%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf "$RPM_BUILD_ROOT"


%files -f INSTALLED_FILES
%defattr(644, root, root)

%doc %{_defaultdocdir}/%{name}

%post
# evil hack to get the directory modes straight
chmod 755 /etc/gnumed
chmod 755 /usr/share/gnumed
chmod 755 /usr/share/gnumed/bitmaps
chmod 755 /usr/lib/python/site-packages/Gnumed
chmod 755 /usr/lib/python/site-packages/Gnumed/business
chmod 755 /usr/lib/python/site-packages/Gnumed/exporters
chmod 755 /usr/lib/python/site-packages/Gnumed/pycommon
chmod 755 /usr/lib/python/site-packages/Gnumed/wxGladeWidgets
chmod 755 /usr/lib/python/site-packages/Gnumed/wxpython
chmod 755 /usr/lib/python/site-packages/Gnumed/wxpython/gui
chmod 755 /usr/bin/gnumed

%changelog -n gnumed-client
* Sun Oct 21 2007 - sebastian.hilbert@gmx.net
- usable version, some weird hacks removed

* Sun Jun 03 2007 - sebastian.hilbert@gmx.net
- Initial creation of package gnumed-client (GNUmed).
