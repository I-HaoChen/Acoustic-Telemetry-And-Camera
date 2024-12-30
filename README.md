# Acoustic tags versus camera - A Case Study on Feeding Behaviour of European seabass in Sea Cages 
Code for the paper: Acoustic tags versus camera - A Case Study on Feeding Behaviour of European seabass in Sea Cages

Author of this repository: I-Hao Chen

## Citation

This repository: [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12997571.svg)](https://doi.org/10.5281/zenodo.12997571)

The paper using this repository can be found here: 10.3389/fmars.2024.1497336 

The dataset for the code and paper is located under the DOI: 

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.12999133.svg)](https://doi.org/10.5281/zenodo.12999133)

## Installation

For installation on local machine, run:
```
pip install git+https://github.com/I-HaoChen/Acoustic-Telemetry-And-Camera.git
```
or clone the whole repository, make sure to have all required packages installed and install with
```
git clone git@github.com:I-HaoChen/Acoustic-Telemetry-And-Camera.git
cd Acoustic-Telemetry-And-Camera; pip install -r requirements.txt; pip install -e .
```
Open the python console.
To plot the Figures (the ones who use data) from the paper run:
```
from src.create_paper_figures import create_paper_figures
create_paper_figures()
```

## License
Licensing note: The written code is under the Apache License Version 2.0 

(see LICENSE file or  [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0))

Some files, however, were originally licensed under the MIT license and have therefore the MIT license in their header

(see LICENSE.mit or  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT))

## Ethics statement
Note that part of this repository was heavily inspired by the repository under [![DOI](https://zenodo.org/badge/604184268.svg)](https://zenodo.org/badge/latestdoi/604184268)
which belongs to the paper under [![DOI](https://zenodo.org/badge/DOI/10.3389/fmars.2023.1168953.svg)](https://doi.org/10.3389/fmars.2023.1168953)

or https://www.frontiersin.org/journals/marine-science/articles/10.3389/fmars.2023.1168953.

Especially loading, filtering, and preprocessing functions and dataframe structure will be similar or same, as the loaded acoustic transmitter dataset types were similar or same in both respective studies.
