.. image:: images/orochi_icon.png
   :align: center
   :width: 80px
   :target: https://github.com/Tominaka-Laboratory/orochi.view
   :alt: Orochi Logo

===========
orochi.view
===========

.. |title| replace:: orochi.view
.. _title: https://Tominaka-Laboratory.github.io/orochi.view

.. |Icon| image:: images/orochi_icon.png
   :target: https://github.com/Tominaka-Laboratory/orochi.view
   :height: 100px

|PyPi| |Forge| |PythonVersion| |ChemRxiv| |PR|

|CI| |Codecov| |Black| |Tracking|

.. |ChemRxiv| image:: https://img.shields.io/badge/ChemRxiv-10.26434%2Fchemrxiv.15010802%2Fv2-blue.svg
        :target: https://doi.org/10.26434/chemrxiv.15010802/v2

.. |Black| image:: https://img.shields.io/badge/code_style-black-black
        :target: https://github.com/psf/black

.. |CI| image:: https://github.com/Tominaka-Laboratory/orochi.view/actions/workflows/tests.yml/badge.svg
        :target: https://github.com/Tominaka-Laboratory/orochi.view/actions/workflows/tests.yml

.. |Codecov| image:: https://codecov.io/gh/Tominaka-Laboratory/orochi.view/branch/main/graph/badge.svg
        :target: https://codecov.io/gh/Tominaka-Laboratory/orochi.view

.. |Forge| image:: https://img.shields.io/conda/vn/conda-forge/orochi.view
        :target: https://anaconda.org/conda-forge/orochi.view

.. |PR| image:: https://img.shields.io/badge/PR-Welcome-29ab47ff

.. |PyPi| image:: https://img.shields.io/pypi/v/orochi.view
        :target: https://pypi.org/project/orochi.view/

.. |PythonVersion| image:: https://img.shields.io/pypi/pyversions/orochi.view
        :target: https://pypi.org/project/orochi.view/

.. |Tracking| image:: https://img.shields.io/badge/issue_tracking-github-blue
        :target: https://github.com/Tominaka-Laboratory/orochi.view/issues

Interactive Data and Structural Visualization for the Orochi Ecosystem
======================================================================

The ``orochi.view`` package serves as the **dedicated visualization toolkit** within the Orochi framework. It provides interactive, publication-quality 2D/3D visual inspection components tailored specifically for **atomic crystallographic structures**, **nanoparticles**, **low-dimensional materials (2D nanosheets)**, and **X-ray/neutron scattering profiles** (such as the Pair Distribution Function, *G(r)*).

Key Capabilities
----------------

* **Interactive 3D Structure Viewer (``py3Dmol`` & WebGL)**:
  Encapsulated in the ``ModelViewer`` class (``orochi.view.model_viewer``), this component enables high-performance WebGL rendering of atomic lattices, unit cell boundaries, bonds, and coordination envelopes. Inheriting directly from ``orochi.base.core.OrochiBase``, the viewer dynamically syncs with structural parameters defined in ``orochi.phase``, allowing immediate visual updates in Gradio web interfaces when parameters are adjusted.

* **Dynamic Total Scattering & PDF Plots (``Plotly``)**:
  Through ``orochi.view.pdf``, users can render interactive, responsive Plotly figures comparing observed and simulated data (*G(r)*, *F(Q)*, *S(Q)*). Features include real-time fit difference profiles ($\Delta G(r)$), synchronized zoom and hover tooltips, and customizable plotting layouts optimized for both standalone notebooks and web GUIs.

* **Optimization & Bayesian Parameter Landscape Diagnostics (``Optuna`` & ``Plotly``)**:
  Diagnostic plots for Bayesian global optimization and least-squares refinement, including hyperparameter importance rankings, slice diagrams, and optimization objective histories (``orochi.view.optuna.plots``).

Package Status & Future Roadmap
-------------------------------

.. note::
   **Active Development & Architectural Evolution:**
   ``orochi.view`` brings together visualization components developed alongside diverse Orochi workflows. Because visualization and user interaction are tightly coupled with the interactive web interface (``orochi.ui``) and individual computational domains, many aspects of this package remain under active development and experimental consolidation.
   
   Depending on future design refinements, components of ``orochi.view`` may be reorganized, streamlined, or directly integrated into ``orochi.ui`` and respective core calculation packages in subsequent releases.

Installation
------------

Using ``pip``:

::

    pip install orochi.view

From source:

::

    git clone https://github.com/Tominaka-Laboratory/orochi.view.git
    cd orochi.view
    pip install -e .

To confirm the installation was successful, run:

::

    python -c "import orochi.view; print(orochi.view.__version__)"

Quick Start
-----------

**1. 3D Atomic Structure Visualization with ModelViewer**

::

    from orochi.phase import Phase
    from orochi.view.model_viewer import ModelViewer

    # Load crystallographic structure
    phase = Phase()
    phase.read_cif("CeO2.cif")

    # Render interactive 3D WebGL model
    viewer = ModelViewer()
    html_output = viewer.view_model(phase)

**2. Interactive PDF Comparison with Plotly**

::

    from orochi.view.pdf import interactive

    # Plot experimental vs. simulated G(r)
    fig = interactive.plot(
        r_obs, g_obs,
        r_sim, g_sim,
        title="CeO2 PDF Refinement"
    )
    fig.show()

Support and Contribute
----------------------

The orochi.view project welcomes your expertise and enthusiasm!
If you see a bug or want to request a feature, please `report it as an issue <https://github.com/Tominaka-Laboratory/orochi.view/issues>`_ and/or `submit a fix as a PR <https://github.com/Tominaka-Laboratory/orochi.view/pulls>`_.

Before contributing, please read our `Code of Conduct <https://github.com/Tominaka-Laboratory/orochi.view/blob/main/CODE_OF_CONDUCT.rst>`_.

License
-------

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. See the ``LICENSE.rst`` file for details.

Citation
--------

If you use Orochi in your research, please cite:

.. code-block:: bibtex

    @article{tominaka2026orochi,
      title   = {Orochi: A Physics-Grounded Python Package for Pair Distribution Function Analysis of Crystalline and Low-Dimensional Materials},
      author  = {Tominaka, Satoshi},
      journal = {ChemRxiv},
      year    = {2026},
      doi     = {10.26434/chemrxiv.15010802/v2},
      url     = {https://doi.org/10.26434/chemrxiv.15010802/v2}
    }

Contact
-------

For questions or feedback, please open a GitHub issue or contact Dr. Satoshi Tominaka at tominaka.satoshi@nims.go.jp.
