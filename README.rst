======================
Web Automation Toolkit
======================

Automation tools for simple web accounts operations. Currently supports:

- Daily XiaMi_ check-ins
- Monthly No-IP_ free hostname refreshes

.. _XiaMi: http://www.xiami.com/
.. _No-IP: https://www.noip.com/

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
