Release Procedure
=================

Version Numbering
-----------------

Releases have a ``<major>.<minor>.<patch>`` versioning scheme, and broadly
follow the `Semantic Versioning`_ conventions:

* Changes to the major version number indicate backwards-incompatible changes
  to the feature set and/or interface;
* Changes to the minor version indicate backwards-compatible feature
  enhancements;
* Changes to the patch version indicate backwards-compatible bug fixes.

There is no formal end-of-life for Comet releases, but generally only critical
bugs will be fixed in major or minor versions earlier than the most recent
release.

.. _Semantic Versioning: http://semver.org/

Making a Release
----------------

Major and minor releases happen on a branch named ``release-N.M``, where ``N``
is the major version number and ``M`` the minor. Create the branch as
follows::

  $ git checkout -b release-N.M

Patch releases happen on existing branches. Check out the branch as follows::

  $ git checkout release-N.M

The release will correspond to a particular commit in which we set the version
number. After all the other commits which will constitute the release have
been committed to the release branch, edit the file ``comet/__init__.py`` and
set the ``__version__`` variable appropriately. Also make sure the release
history page ``docs/appendix/history.rst`` contains the date of the new
release. Commit this change with an appropriate log message::

  $ vim comet/__init__.py
  $ vim docs/appendix/history.rst
  $ git commit comet/__init__.py -m "Set version N.M.P"

Next tag the release with the version number::

  $ git tag -a "N.M.P" -m "Comet release N.M.P"

Push everything, including the tag, to GitHub::

  $ git push --tags origin release-N.M

Visit the `ReadTheDocs Dashboard
<https://readthedocs.org/dashboard/comet/versions/>`_ and ensure that the
release branch is marked as active (i.e. that documentation for that branch
will be built). Normally, the most recent release should be marked as the
"default version".

Push an update to `PyPI <http://pypi.python.org>`_. Should be as simple as::

  $ python setup.py sdist upload.

Chance back to the ``master`` branch and increment the version number to
indicate that it is now a pre-release of the next version of Comet (e.g.,
``N.M+1.0-pre``). Make sure that the release history is correct here too.
Commit and push.

E-mail an announcement to the IVOA Time Domain Interest Group `mailing list
<http://www.ivoa.net/mailman/listinfo/voevent>`_.
