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

Installation proceeds as follows::

  $ vi comet.sh                # Customise to local requirements
  $ cp comet.sh /etc/init.d
  $ update-rc.d comet defaults
