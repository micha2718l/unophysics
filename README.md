
# UNO Physics Tools

UNO Physics Tools is a Python package combining quantum mechanics utilities, wavelet-based signal processing, Jupyter notebook helpers, and specialized tools for reading and analyzing LADC GEMM audio data (including a GUI for exploration). Developed at the University of New Orleans.

## Installation
---------------
It is recommended to use a virtual environment:
```sh
python -m venv venv
source venv/bin/activate
```
To install:
- Clone this repo and install:
  ```sh
  git clone https://github.com/micha2718l/unophysics.git
  cd unophysics
  pip install .
  ```
- Or install directly with pip:
  ```sh
  pip install unophysics
  ```

To use LADC data access, you must provide a `unophysics.cred` file with server credentials (see `unophysics/_config.py` for details).

## Features
--------
- **Quantum Mechanics Utilities**: Symbolic computation of Hamiltonians, energies, and wavefunctions using SymPy.
- **Wavelet Signal Processing**: Denoising and cleaning of signals with PyWavelets and NumPy.
- **Jupyter Notebook Helpers**: Functions for pretty-printing math and Markdown in notebooks.
- **LADC GEMM Audio Tools**:
  - Read, process, and visualize LADC GEMM audio files.
  - Access and search remote data via MongoDB and FTP (requires credentials).
  - GUI for interactive exploration (`python -m unophysics` launches a Tkinter-based app).
- **Marine Mammal Data**: Built-in reference data for Bryde’s whale calls and frequency ranges.

## Usage Examples
-----------------
```python
# Quantum mechanics: compute a wavefunction
from unophysics import quantum
psi = quantum.phi(n=2, a=1)

# Wavelet denoising
from unophysics import wavefuncs
cleaned = wavefuncs.wave_clean(data)

# Notebook pretty-printing
from unophysics import nbtools
nbtools.pmath(psi)

# LADC audio file: load and plot
from unophysics import ladc
ears = ladc.EARS('sample_data/71621DC7.190')
import matplotlib.pyplot as plt
plt.plot(ears.data)
plt.show()
```

To launch the GUI for LADC file exploration:
```sh
python -m unophysics
```

## Directory Structure
---------------------
- `unophysics/`: Main package code (quantum, wavelet, notebook, and LADC tools)
- `sample_data/`: Example LADC audio file
- `tests/`: Unit tests for each module
- `docs/`: Sphinx documentation sources

## License
-------
Free software: MIT license

## Contributing and Testing
---------------------------
See `CONTRIBUTING.md` for guidelines.

To run tests:
```sh
pytest
# or
tox
```

## Credits
-------
Most of this work has been done by various students and professors at the University of New Orleans Physics department.
Special thanks to the [LADC GEMM Consortium](http://www.ladcgemm.org/) for data to work with and inspire us.
This package was created with:
- [Cookiecutter](https://github.com/audreyr/cookiecutter) and the
- [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
- Relies heavily on numpy, PyWavelets, scipy, etc.
