================
 Change history
================

Note: Changelog prior to 1.0.0 is patchy.

1.0.1 (unreleased)
==================

* Add metadata-driven GitHub checks for the latest published stable release,
  with optional GITHUB_TOKEN authentication.
* Report only the highest discovered version in quiet text output, after
  pre-release filtering; retain all matching versions in structured output.
* Update ebuild path handling for Portage shell-quoting and repository-list changes.
* Add GitLab and Gitea/Forgejo release handlers.
* Switch PyPI release discovery to the JSON API.
* Use direct upstream URLs for PyPI and RubyGems handler detection.
* Remove obsolete BerliOS, Freecode, and Google Code handlers.
* Remove euscanwww
* Remove man page
* Major reformatting with black and isort
* Migrate to a PEP517 buildsystem
* Add python 3.12 support
* Change default user-agent
* Use portage MetadataXML over gentoolkit Metadata after it was removed in gentoolkit version 0.6.0.

1.0.0 (released 2020-09-16)
===========================

* Python 3 compatibility
* Fix brute-force short option
* Beautiful Soup 4 support

0.1.1 (released 2012-01-18)
===========================

* Better --quiet mode

0.1.0 (released 2011-11-27)
===========================

* Initial Release
