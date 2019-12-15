[![Build Status](https://travis-ci.org/micha2718l/unophysics.svg?branch=master)](https://travis-ci.org/micha2718l/unophysics)

# UNO Physics Tools
-------------------
- Python tools collected from data analysis projects at the University of New Orleans.
- Some of these will be useful in general, some will be specific to our internal systems.
  - TODO: seperate the generally useful parts from the specific parts.
- TODO: add in proper badges

## Installation
---------------
- Recommended to use a virtualenv. `python -m virtualenv *name of directory to put venv*`
- To install:
  - Either clone this repo then install:
    - `git clone https://github.com/micha2718l/unophysics.git`
    - `cd unophysics`
    - `pip install .`
  - Or use `pip`
    - `pip install unophysics`

## Tools for physics from UNO.
------------------------------
- Free software: MIT license
- Documentation: TODO

## Features
--------
- Wavelet noise cleaning function
- Various quantum mechanics formulas implemented
- Jupyter Notebook helper functions for displaying math
- Can load LADC GEMM data, for the data access functions to work, credentials for the servers are needed. Contact us if that is desired. 
- Can work with the LADC GEMM data to display spectrographic information
- Data on various marine mammal species built into the library (currently has Bryde's whale information, in progress to fill in with Fin whale data).
- TODO: Examples

## Credits
-------
- Most of this work has been done by various students and professors at the University of New Orleans Physics department.
- Special thanks to the [LADC GEMM Consortium](http://www.ladcgemm.org/) for data to work with and inspire us.
- This package was created with:
  - [Cookiecutter](https://github.com/audreyr/cookiecutter) and the
  - [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
  - relies heavily on numpy, PyWavelets, scipy, etc...
