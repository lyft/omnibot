############
Contributing
############

***************
Code of conduct
***************

This project is governed by `Lyft's code of conduct <https://github.com/lyft/code-of-conduct>`_.
All contributors and participants agree to abide by its terms.

*****************
Contributing code
*****************

Sign the Contributor License Agreement (CLA)
============================================

We require a CLA for code contributions, so before we can accept a pull request
we need to have a signed CLA. Please `visit our CLA service <https://oss.lyft.com/cla>`_
follow the instructions to sign the CLA.

File issues in Github
=====================

In general all enhancements or bugs should be tracked via github issues before
PRs are submitted. We don't require them, but it'll help us plan and track.

When submitting bugs through issues, please try to be as descriptive as
possible. It'll make it easier and quicker for everyone if the developers can
easily reproduce your bug.

Submit pull requests
====================

Our only method of accepting code changes is through github pull requests.

Adding new dependencies to requirements
=======================================

We freeze python dependencies from direct dependencies (from ``requirements.in``),
to diamond dependencies (in ``requirements.txt``). Doing so ensures a consistent installation
with well known versions in test environments, out to production environments.

If you need to add a dependency, or update the version of a dependency, you should modify
``requirements.in``. After doing so, you can compile the in file into the txt file using
``pip-compile.sh``.

.. code-block:: bash

   ./pip-compile.sh
   # or: make compile_deps

Approving licenses or dependencies
==================================

We run a `license scanner/approver <https://github.com/pivotal/LicenseFinder>`_ for third-party
dependencies used by omnibot. If you add or upgrade dependencies in ``requirements.in`` or
``requirements.txt``, the license scanner tests may fail, outputing the failed requirement, and
its associated license. As long as the license is acceptable, a project owner will approve the
license for use.

You'll need docker to approve licenses or dependencies. Commands below assume you're in the omnibot
repo root folder.

To approve a new license:

.. code-block:: bash

   docker run -v $PWD:/scan -it licensefinder/license_finder /bin/bash -lc "cd /scan && license_finder whitelist add <license_to_add>"

To assign a license to a dependency that's listed as unknown (preferred method of handling unknown licenses):

.. code-block:: bash

   docker run -v $PWD:/scan -it licensefinder/license_finder /bin/bash -lc "cd /scan && license_finder dependencies add <unknown_dependency> <LICENSE> --homepage='https://link.to.dependency/'"

To approve a new dependency, that has a license that's not easy to add (dual or multi-licensed, conditionally licensed, etc.):

.. code-block:: bash

   docker run -v $PWD:/scan -it licensefinder/license_finder /bin/bash -lc "cd /scan && license_finder approvals add <dependency_to_add> --why 'Description of why the License is acceptable'"
