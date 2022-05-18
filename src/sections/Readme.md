# Readme

This directory contains all jupyter notebooks prefixed by `s<number>` and should be read in chronological order for best understanding. To be able to import classes and methods from jupyter notebook in a fast and easy way, all notebooks contain the following code at the beginning 

```
%load_ext autoreload
%autoreload 2

from utils.jupyer_loader import JupyerLoader

loader = JupyterLoader()
loader.load_all()
```

The jupyter loader is a script written by us in `utils/jupyter_loader.py` and will convert all jupyter notebooks to python scripts that are put in the `converted_notebooks` directory. The script only exports python cells that are not marked with the `no-python-export` tag. Therefore every cell that does not contain code for usage in other notebooks (for instance test code) should be marked with this tag to speed up import.

The first two lines will prevent caching of python scripts. Therefore, whenever a change was made in a previous notebook, the cell with the jupyter loader should be excuted again to export the new changes to python. Through the use of `autoreload` the new changes will then be picked up automatically.

In later chapters, some code is introduced for performance measurements that takes very long time to run. Therefore the results of these code cells are cached in the `results` directory. If you need to rerun the code, delete the corresponding cache file first.