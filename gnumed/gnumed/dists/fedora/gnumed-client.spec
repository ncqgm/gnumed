Name:           gnumed-client
Version:        1.8.25
Release:        %{autorelease}
Summary:        Electronic medical record system client

%global mainversion %(echo %{version} | cut --complement -d . -f 3)

License:        GPL-2.0-or-later AND GPL-3.0-only AND LicenseRef-Fedora-Public-Domain AND CC-BY-SA-3.0
URL:            https://www.gnumed.de
Source:         %{url}/downloads/client/%{mainversion}/gnumed-client.%{version}.tgz
BuildArch:      noarch

BuildRequires:  desktop-file-utils
BuildRequires:  gettext
BuildRequires:  libappstream-glib
BuildRequires:  python3-devel
BuildRequires:  systemd-rpm-macros
Requires:  coreutils
Requires:  file
Requires:  google-noto-color-emoji-fonts
Requires:  gnumed-common
Requires:  gzip
Requires:  hicolor-icon-theme
Requires:  hunspell
Requires:  ImageMagick
Requires:  mc
Requires:  openssl
Requires:  postgresql-client
Requires:  python3
Requires:  python3-enchant
Requires:  python3-hl7
Requires:  python3-httplib2
Requires:  python3-gnuplot
Requires:  python3-lxml
Requires:  python3-psutil
Requires:  python3-psycopg2
Requires:  python3-pyudev
Requires:  python3-standard-mailcap
Requires:  python3-wxpython4
Requires:  texlive
Requires:  wget
Recommends:  audiofile
Recommends:  dcmtk or aeskulap or amide or dicomscope or imagej or xmedcon
Recommends:  perl-Image-ExifTool
Recommends:  xsane
Recommends:  libextractor
# Maybe it is possible to use chrony for synchronization?
Recommends:  ntpsec
Recommends:  firefox or chromium or dillo or w3m or falkon or surf or vimb or lynx or epiphany or elinks or konqueror
Recommends:  libreoffice-writer
# Need to package in Fedora
# https://codeberg.org/toddy/medicalterms
# https://salsa.debian.org/med-team/medicalterms
#Recommends:  wgerman-medical
Recommends:  xdg-utils
Recommends:  texlive-collection-latexextra
Recommends:  pdftk-java
Recommends:  python3-vobject
# Not on Fedora, and unmaintained, perhaps replace with something else
#Recommends:  python3-pyqrcode
Recommends:  python3-unidecode
Recommends:  python3-docutils
Recommends:  7zip
Recommends:  gnupg2
Recommends:  poppler-utils
Recommends:  qpdf
Recommends:  texlive-lacheck
Recommends:  texlive-chktex
Suggests:  korganizer
Suggests:  libchipcard
Suggests:  incron
Suggests:  gnumed-server
Suggests:  akonadi-calendar-tools
Suggests:  gimp or kolourpaint
# Ubuntu/Debian specific package
# https://salsa.debian.org/debian-edu-pkg-team/shutdown-at-night
#Suggests:  shutdown-at-night
# Not yet packaged for Fedora
# https://gitlab.com/Teuniz/EDFbrowser
# Ubuntu package
# https://salsa.debian.org/med-team/edfbrowser
# Suggests:  edfbrowser
Suggests:  autokey-qt or autokey-gtk
# wakeonlan https://github.com/jpoliv/wakeonlan/ is not in Fedora, licensing?
# etherwake is not in Fedora, though is in Debian
# https://salsa.debian.org/debian/etherwake
#Suggests:  wakeonlan or etherwake
# nvram-wakeup is not in Fedora
# https://sourceforge.net/projects/nvram-wakeup/
#Suggests:  nvram-wakeup
Suggests:  entangle
# Unmaintained
# https://github.com/elbow-jason/Uno-deprecated
# consider using
# https://pypi.org/project/html-creator/
# https://pypi.org/project/tinyhtml/
# https://pypi.org/project/yattag/
#Suggests:  python3-uno
# Not packaged in Fedora
# Sources available from Debian
# https://salsa.debian.org/med-team/qrisk2
#Suggests:  qrisk2

%description
A free, libre, open source electronic medical record management
system client application.


%package -n gnumed-common
Summary:    Files used by both GNUmed-client and GNUmed-server
BuildArch:  noarch
Requires:   python3-psycopg2
Suggests:   dmtx-utils or iec16022

%description -n gnumed-common
Files used by both GNUmed-cliant and GNUmed-server.

%package de
Summary:    Files for services used in Germany
Requires:   gnumed-client
# Not yet packaged
#Recommends: wgerman-medical
Recommends: hunspell-de
# Not yet packaged
# Recommends:  hunspell-de-med
Recommends: dmtx-utils or iec16022
Recommends: libchipcard
# Not packaged in Fedora
# http://sourceforge.net/projects/ctapi-mkt
# https://salsa.debian.org/med-team/libctapimkt
#Suggests:  libctapimkt1
BuildArch:  noarch

%description de
Files for services used in Germany.

%prep
%autosetup -n gnumed-client.%{version}

# Regenerate translation files
rm client/po/*.mo

%build
# compile translations
for POFILE in client/po/*.po; do
  echo "Compiling $file"
  LANG=$(basename $POFILE .po)
  MOFILE=gnumed.mo
  mkdir client/po/${LANG}
  msgfmt --statistics -o client/po/${LANG}/${MOFILE} ${POFILE}
done


%install
mkdir -p %{buildroot}%{_datadir}/gnumed/Gnumed
install -Dm 0644 client/gnumed.py %{buildroot}%{_datadir}/gnumed/Gnumed/gnumed.py
cp -p -r client/business  %{buildroot}%{_datadir}/gnumed/Gnumed/business
cp -p -r client/exporters  %{buildroot}%{_datadir}/gnumed/Gnumed/exporters
cp -p -r client/importers  %{buildroot}%{_datadir}/gnumed/Gnumed/importers
cp -p -r client/wxpython  %{buildroot}%{_datadir}/gnumed/Gnumed/wxpython
cp -p -r client/wxGladeWidgets  %{buildroot}%{_datadir}/gnumed/Gnumed/wxGladeWidgets
install -Dm 0755 client/gnumed  %{buildroot}%{_bindir}/gnumed
install -Dm 0755 external-tools/gm-convert_file  %{buildroot}%{_bindir}/gm-convert_file
install -Dm 0755 external-tools/gm-create_datamatrix  %{buildroot}%{_bindir}/gm-create_datamatrix
install -Dm 0755 external-tools/gm-describe_file  %{buildroot}%{_bindir}/gm-describe_file
install -Dm 0755 external-tools/gm-import_incoming  %{buildroot}%{_bindir}/gm-import_incoming
install -Dm 0755 external-tools/gm-print_doc  %{buildroot}%{_bindir}/gm-print_doc
install -Dm 0644 client/connectors/gm_ctl_client.conf	%{buildroot}%{_sysconfdir}/gnumed/gm_ctl_client.conf
install -Dm 0644 client/bitmaps/empty-face-in-bust.png %{buildroot}%{_datadir}/gnumed/bitmaps/empty-face-in-bust.png
install -Dm 0644 client/bitmaps/gm_icon-serpent_and_gnu.png %{buildroot}%{_datadir}/gnumed/bitmaps/gm_icon-serpent_and_gnu.png
install -Dm 0644 client/bitmaps/gnumedlogo.png %{buildroot}%{_datadir}/gnumed/bitmaps/gnumedlogo.png
install -Dm 0644 client/bitmaps/serpent.png %{buildroot}%{_datadir}/gnumed/bitmaps/serpent.png
install -Dm 0644 client/bitmaps/gm_icon-serpent_and_gnu.svg  %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/gm_icon-serpent_and_gnu.svg
install -Dm 0644 client/bitmaps/gm_icon-serpent_and_gnu.png  %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/gm_icon-serpent_and_gnu.png
install -Dm 0644 client/gnumed_client.desktop  %{buildroot}%{_datadir}/applications/gnumed_client.desktop
install -Dm 0755 external-tools/gm-download_data  %{buildroot}%{_datadir}/gnumed/bin/gm-download_data
cp -p -r client/timelinelib %{buildroot}%{_datadir}/gnumed/Gnumed/timelinelib
cp -p -r client/tlicons  %{buildroot}%{_datadir}/gnumed/Gnumed/tlicons
install -Dm 0644 client/appdata.xml %{buildroot}%{_metainfodir}/gnumed_client.appdata.xml

# Install man pages
install -Dm 0644 client/doc/gnumed.1 %{buildroot}%{_mandir}/man1/gnumed.1*
install -Dm 0644 client/doc/gm-convert_file.1 %{buildroot}%{_mandir}/man1/gm-convert_file.1*
install -Dm 0644 client/doc/gm-create_datamatrix.1 %{buildroot}%{_mandir}/man1/gm-create_datamatrix.1*
install -Dm 0644 client/doc/gm-describe_file.1 %{buildroot}%{_mandir}/man1/gm-describe_file.1*
install -Dm 0644 client/doc/gm-import_incoming.1 %{buildroot}%{_mandir}/man1/gm-import_incoming.1*
install -Dm 0644 client/doc/gm-print_doc.1 %{buildroot}%{_mandir}/man1/gm-print_doc.1*
install -Dm 0644 client/doc/gm_ctl_client.1 %{buildroot}%{_mandir}/man1/gm_ctl_client.1*

# Install translations
for POFILE in client/po/*.po; do
  LANG=$(basename $POFILE .po)
  MOFILE=gnumed.mo
  mkdir -p %{buildroot}%{_datadir}/locale/${LANG}/LC_MESSAGES
  install -Dm 0644  client/po/${LANG}/${MOFILE}  %{buildroot}%{_datadir}/locale/${LANG}/LC_MESSAGES/${MOFILE}
done
%find_lang gnumed

# common files

cp -p -r client/pycommon %{buildroot}/%{_datadir}/gnumed/Gnumed
install -Dm 0644 client/__init__.py %{buildroot}%{_datadir}/gnumed/Gnumed/__init__.py
install -Dm 0644 client/gnumed-client.tmpfiles.d.conf %{buildroot}%{_tmpfilesdir}/gnumed-client.tmpfiles.d.conf
install -d -m 0755 %{buildroot}/run/gnumed-client/
touch %{buildroot}/run/gnumed-client.pid
chmod 0644 %{buildroot}/run/gnumed-client.pid

# German client
install -Dm 0755 external-tools/gm-download_atc   %{buildroot}%{_datadir}/gnumed/bin/gm-download_atc

%check
desktop-file-validate %{buildroot}/%{_datadir}/applications/gnumed_client.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/gnumed_client.appdata.xml

%files -f gnumed.lang
%license client/COPYING.timeline
%license client/COPYING.timeline.icons
%license client/COPYING.TangoDesktopProject
%doc client/README
%doc client/README.timeline
%doc client/CHANGELOG
%doc client/doc/hook_script_example.py
%{_bindir}/gnumed
%{_bindir}/gm-convert_file
%{_bindir}/gm-create_datamatrix
%{_bindir}/gm-describe_file
%{_bindir}/gm-import_incoming
%{_bindir}/gm-print_doc
%dir %{_sysconfdir}/gnumed
%{_sysconfdir}/gnumed/gm_ctl_client.conf
%{_datadir}/gnumed/
%{_datadir}/applications/gnumed_client.desktop
%{_metainfodir}/gnumed_client.appdata.xml
%{_datadir}/icons/hicolor/scalable/apps/gm_icon-serpent_and_gnu.svg
%{_datadir}/icons/hicolor/128x128/apps/gm_icon-serpent_and_gnu.png
%{_mandir}/man1/gnumed.1*
%{_mandir}/man1/gm-convert_file.1*
%{_mandir}/man1/gm-create_datamatrix.1*
%{_mandir}/man1/gm-describe_file.1*
%{_mandir}/man1/gm-import_incoming.1*
%{_mandir}/man1/gm-print_doc.1*
%{_mandir}/man1/gm_ctl_client.1*

%files -n gnumed-common
%license client/LICENSE
%license client/GnuPublicLicense.txt
%dir %{_datadir}/gnumed/Gnumed
%{_datadir}/gnumed/Gnumed/__init__.py
%dir /run/gnumed-client/
%verify(not size mtime md5) /run/gnumed-client.pid
%{_tmpfilesdir}/gnumed-client.tmpfiles.d.conf

%files de
%{_datadir}/gnumed/bin/gm-download_atc

%changelog
%autochangelog
