======================
Web Automation Toolkit
======================

Automation tools for simple web accounts operations. Currently supports:

- Daily `XiaMi <http://www.xiami.com/>`_ check-ins
- Monthly `No-IP <https://www.noip.com/>`_ free hostname refreshes
- Semi-automatic advancing for taking online defensive driver's course (DDC) at `New York Safety Council <https://www.newyorksafetycouncil.com/>`_

******************
About Requirements
******************

Besides requirements.txt listing, please also make sure the following are installed:

- ``Firefox``: for ``selenium``'s headful operation,
- ``PhantomJS``: for ``selenium``'s headless operation, and
- ``Postbox`` (or other smtp server): for ``smtplib`` to be able to send email upon errors.

***********
Usage Notes
***********

Use flag ``--help`` or ``-h`` for general usage help.

For command-line password input (with flag ``--password-now``), do not start the script in background; consider using ``screen`` instead.

For gui password input (with flag ``--no-password-now``), starting in background is fine.

Because the DDC mode is more of a quick hack where real-time human intervention is needed every now and then, head-less mode is disabled.
