
# OTTO (version with wind)

This is a variant of [OTTO](https://github.com/C0PEP0D/otto) for the 2D setup with wind, for benchmarking purposes. 
It will be merged into OTTO in a near future.

## Installation

### Requirements

OTTO requires Python 3.8 or greater.
Dependencies are listed in [requirements.txt](https://github.com/C0PEP0D/otto/blob/main/requirements.txt),
missing dependencies will be installed automatically.

### Conda users

If you use conda to manage your Python environments, you can install OTTO in a dedicated environment `ottoenv`

``` bash
conda create --name ottoenv python=3.8
conda activate ottoenv
```

### Installing

``` bash
python3 setup.py install
```

## Training

Go to the `otto/learn` directory and train the NN using
``` bash
python3 learn.py -i param.py
```
where `param.py` is the name of a parameter file located in the `parameters` directory.

