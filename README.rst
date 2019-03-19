======================
CharIoT Privacy Engine
======================

|epl|_

Runtime privacy engine and service is a part of the CHARIOT architecture that ensures that data transmitted from the safety critical system to the IoT will not compromise sensitive information. 

The Privacy Engine analyses a model of the interactions between the controlled safety critical system and the IoT system and by using model-based information security techniques ensures that no sensitive information is exposed in locations where it can be accessed by third/unauthorized parties. 

Features
--------

* Inspect message
* Apply encryption for packages
* Trace logs

Installation
------------

TBC

Developer Manual
----------------

Build docker images
~~~~~~~~~~~~~~~~~~~

Following commands use to make a new release.

.. code-block:: shell

    docker login registry.gitlab.com
    docker build -t registry.gitlab.com/chariot-h2020/chariot-privacy-engine .
    docker push registry.gitlab.com/chariot-h2020/chariot-privacy-engine


Credits
-------

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.

.. |epl| image:: https://img.shields.io/badge/License-EPL-green.svg
.. _epl: https://opensource.org/licenses/EPL-1.0