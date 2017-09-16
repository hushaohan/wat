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

Please make sure the following non-python dependencies are installed:

- ``Firefox``: for ``selenium``'s headful operation (or feel free to change the code to use your preferred ``selenium`` -compatible browser),
- ``PhantomJS``: for ``selenium``'s headless operation, and
- ``Postfix`` (or other smtp server): for ``smtplib`` to be able to send notification emails upon errors.

***********
Usage Notes
***********

Use flag ``--help`` or ``-h`` for general usage help.

For command-line password input (with flag ``--password-now``), do not start the script in background; consider using ``screen`` instead.

For GUI password input (with flag ``--no-password-now``), starting in background is fine.

Because the DDC mode is more of a quick hack where real-time human intervention is needed every now and then, the following settings will be automatically set regardless of user inputs:

- ``headless`` mode: disabled
- ``persistent_session`` mode: enabled
- ``notification_method``: set to ``beep`` (i.e. the ascii ``'\a'`` character)

The flag ``--force`` can be used to override them.
