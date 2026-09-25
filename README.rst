What is euscan-ng ?
===================

dev-portage/euscan-ng
=====================

euscan-ng is a fork of Bernard Cafarelli's euscan: https://github.com/voyageur/euscan
which is a fork of Corentin Chary's euscan: https://github.com/iksaif/euscan

Right now euscan-ng and (legacy) euscan cannot be installed (system-wide) on the same system.
euscan-ng is available in src_prepare overlay as a dev package (app-portage/euscan-ng-9999).

This tool allows to check if a given package has new upstream versions or not.
It will use different heuristic to scan upstream and grab new versions and related urls.

This tool was designed to mimic debian's uscan, but there is a major
difference between the two: uscan uses a specific "watch" file that describes
how it should scan packages, while euscan-ng uses information from ebuilds
and upstream identifiers in metadata.xml.

euscan-ng heuristics are described in the "How does it work ?" section.

Changes in this fork
--------------------

GitHub packages can be checked using their ``github`` remote-id in
``metadata.xml``. The handler checks the latest published stable release and
reports its release page when the version is newer than the ebuild. See
"GitHub metadata" below for setup and limitations.

Quiet text output selects only the highest discovered version per package,
using Portage version ordering. Pre-release filtering is applied before this
selection. Structured output retains all discovered versions that pass the
filters.

Ebuild path handling has also been updated for Portage versions that no longer
provide the private shell-quoting helper or expose a mutable repository list.

Examples
--------
::

    $ euscan amatch

     * dev-ruby/amatch-0.2.7 [gentoo]

    Ebuild: /home/euscan/local/usr/portage/dev-ruby/amatch/amatch-0.2.7.ebuild
    Repository: gentoo
    Homepage: http://flori.github.com/amatch/
    Description: Approximate Matching Extension for Ruby

     * SRC_URI is 'https://rubygems.org/gems/amatch-0.2.7.gem'
     * Using RubyGem API: amatch

    Upstream Version: 0.2.8 http://rubygems.org/gems/amatch-0.2.8.gem

::

    $ euscan rsyslog

     * app-admin/rsyslog-5.8.5 [gentoo]

    Ebuild: /home/euscan/local/usr/portage/app-admin/rsyslog/rsyslog-5.8.5.ebuild
    Repository: gentoo
    Homepage: http://www.rsyslog.com/
    Description: An enhanced multi-threaded syslogd with database support and more.

     * SRC_URI is 'http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.8.5.tar.gz'
     * Scanning: http://www.rsyslog.com/files/download/rsyslog/rsyslog-${PV}.tar.gz
     * Scanning: http://www.rsyslog.com/files/download/rsyslog
     * Generating version from 5.8.5
     * Brute forcing: http://www.rsyslog.com/files/download/rsyslog/rsyslog-${PV}.tar.gz
     * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.8.6.tar.gz ...        [ !! ]
     * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.8.7.tar.gz ...        [ !! ]
     * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.8.8.tar.gz ...        [ !! ]
     * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.0.tar.gz ...        [ ok ]
     * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.10.0.tar.gz ...         [ !! ]
     * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.11.0.tar.gz ...         [ !! ]
     * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.1.tar.gz ...        [ ok ]
     * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.2.tar.gz ...        [ ok ]
     * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.3.tar.gz ...        [ ok ]
     * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.12.0.tar.gz ...         [ !! ]
     * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.4.tar.gz ...        [ !! ]
     * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.5.tar.gz ...        [ !! ]
     * Trying: http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.6.tar.gz ...        [ !! ]

    Upstream Version: 5.9.1 http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.1.tar.gz
    Upstream Version: 5.9.0 http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.0.tar.gz
    Upstream Version: 5.9.3 http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.3.tar.gz
    Upstream Version: 5.9.2 http://www.rsyslog.com/files/download/rsyslog/rsyslog-5.9.2.tar.gz


Configuration
-------------

Settings are read from ``/etc/euscan.conf`` and then ``~/.euscan.conf``;
user settings override system settings. Use an ``[euscan]`` section with
Python literal values (for example, ``True`` for booleans and quoted strings)::

    [euscan]
    quiet = True
    ignore-pre-release = True
    nocolor = True

``ignore-pre-release-if-stable`` filters pre-releases only when the current
ebuild version is stable. Both pre-release filters are disabled by default.
Defaults and blacklists are defined in ``src/euscan/__init__.py``.

GitHub metadata
---------------

Add the repository's ``owner/repository`` identifier inside the package's
``metadata.xml``::

    <pkgmetadata>
      <upstream>
        <remote-id type="github">owner/repository</remote-id>
      </upstream>
    </pkgmetadata>

An override can also be placed at
``metadata/<category>/<package>/metadata.xml`` relative to the working directory.

The handler requests GitHub's ``/repos/owner/repository/releases/latest`` API
endpoint. It does not scan tags or infer the repository from ``SRC_URI``.
Drafts and releases marked as pre-releases are rejected. A leading ``v`` before
a digit is stripped from the release tag, and the resulting version must be
valid for Portage. The reported URL is the release page.

Set the optional ``GITHUB_TOKEN`` environment variable to authenticate API
requests. An API error, a missing release, or an unrecognized version causes
the scan to fail; selecting this metadata handler does not fall back to
directory scanning or brute force.

How does it work ?
==================

euscan has different heuristics to scan upstream and provides multiple
"handlers". First, here is a description of the generic handler.

Scanning directories
--------------------

The first thing to do is to scan directories. It's also what uscan do, but it
uses a file that describe what url and regexp to use to match packages.

euscan uses SRC_URI and tries to find the current version (or part of this version)
in the resolved SRC_URI and generate a regexp from that.

For example for app-accessibility/dash-4.10.1, SRC_URI is::

  mirror://gnome/sources/dasher/4.10/dasher-4.10.1.tar.bz2

euscan will scan pages based on this template::

  http://ftp.gnome.org/pub/gnome/sources/dasher/${0}.${1}/dasher-${PV}.tar.bz2

Then, from that, it will scan the top-most directory that doesn't depend on
the version, and try to go deeper from here.

Brute force
-----------

Like when scanning directories, a template of SRC_URI is built. Then euscan
generate next possible version numbers, and tries to download the url generated
from the template and the new version number.

For example, running euscan on portage/app-accessibility/festival-freebsoft-utils-0.6::

  SRC_URI is 'http://www.freebsoft.org/pub/projects/festival-freebsoft-utils/festival-freebsoft-utils-0.6.tar.gz'
  Template is http://www.freebsoft.org/pub/projects/festival-freebsoft-utils/festival-freebsoft-utils-${PV}.tar.gz
  Generate version from 0.6: 0.7, 0.8, 0.10, ...
  Try new urls: http://www.freebsoft.org/pub/projects/festival-freebsoft-utils/festival-freebsoft-utils-0.7.tar.gz, etc..

Blacklists
----------

euscan uses blacklist for multiple purposes.

BLACKLIST_VERSIONS
  For versions that should not be checked at all. sys-libs/libstdc++-v3-3.4
  is good example because it's a package which version will always be 3.4
  (Compatibility package for running binaries linked against a pre gcc 3.4 libstdc++).

BLACKLIST_PACKAGES
  Some packages are dead, but SRC_URI refers to sources that are still being
  updated, for example: sys-kernel/xbox-sources that uses the same sources as
  vanilla-sources but is not updated the same way.

SCANDIR_BLACKLIST_URLS
  For urls that are not browsable. mirror://gentoo/ is a good example: it's
  both stupid to scan it and very long/expensive.

BRUTEFORCE_BLACKLIST_PACKAGES and BRUTEFORCE_BLACKLIST_URLS
  Disable brute force on those packages and urls. Most of the time it's because
  upstream is broken and will answer HTTP 200 even if the file doesn't exist.

ROBOTS_TXT_BLACKLIST_DOMAINS
  Don't respect robots.txt for matching domains, including SourceForge and GitHub.

Site handlers
-------------

Pecl/PEAR
  A site handler that uses the Pecl/PEAR rest API
  (http://pear.php.net/manual/en/core.rest.php).

Rubygems
  This one uses rubygems's json API
  (http://guides.rubygems.org/rubygems-org-api/)

PyPI
  Uses PyPI's JSON API to find releases and source distributions. A ``pypi``
  remote-id can specify the upstream package name.

GitHub
  Uses the latest stable release API through a ``github`` remote-id, as
  described in "GitHub metadata" above.

GitLab
  Uses the releases API for recognized GitLab URLs.

Gitea / Forgejo
  Uses the releases API for recognized instance URLs, including Codeberg.
  Supported hosts are listed in ``src/euscan/handlers/gitea.py``; GitLab hosts
  are listed in ``src/euscan/handlers/gitlab.py``.

The obsolete BerliOS, Freecode, and Google Code handlers have been removed.
