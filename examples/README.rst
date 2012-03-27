======================
Comet: Example scripts
======================

Init script
-----------

This directory contains an example init script for Comet. It was developed and
tested on a system running Ubuntu 10.04: it will need customization before it
is applicable to other environments.

When these scripts are installed, the command ``invoke-rc.d comet start`` may
then be used to start Comet, and ``invoke-rc.d comet stop`` to shut it down.
These scripts will automatically be run at system startup/shutdown.  Logs will
be stored in ``/var/log/comet``.

For security reasons, Comet should be set to run as an unprivileged user. You
should create this user yourself. On an Ubuntu system, for example::

  $ sudo adduser --system --home /var/run/comet comet

Installation then proceeds as follows::

  $ vi cometh                  # Customise to local requirements
  $ cp comet /etc/init.d
  $ update-rc.d comet defaults
