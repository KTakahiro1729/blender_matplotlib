# blender_matplotlib
matplotlib backend for blender

# dependencies
- numpy version should be over 0.14.
- matploblib should be downloaded with its dependencies.

Above should be installed into the python packed with blender. To use pip for this python, [this stackflow post]( https://blender.stackexchange.com/questions/56011/how-to-use-pip-with-blenders-bundled-python?answertab=votes#tab-top) should be useful.

# how to use
## import

Place this file as a library of blender. This can be done by using the add-on importer.

## use matplotlib.use

```python
import matplotlib
matplotlib.use("module://backend_blender")
import matplotlib.pyplot as plt
```

## use as always!
use as always !!!
