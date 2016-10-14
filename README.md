dnd Previz Cinema4D integration
===============================


Testing
-------

Unittesting is made with [tox](https://tox.readthedocs.io/en/latest/). Make sure the `blender` executable is in your `PATH`.


Development
-----------

Run something similar to `scripts/sync_install.sh` before reloading the plugin in Cinema4D.


Release
-------

Copy the `previz` module into `Py-Previz/res/lib/python/site-packages` and zip the `Py-Previz` folder. Make sure that no stray __pycache__ files lying around. On Linux:

```sh
$ cd /path/to/repo
$ git clean -f -d -X
$ cd cinema4d
$ mkdir -p Py-Previz/res/lib/python/site-packages
$ cp -r ../previz/previz Py-Previz/res/lib/python/site-packages
$ grep __version__ Py-Previz/Py-Previz.pyp
__version__ = "0.0.1"
$ zip -r Py-Previz-v0.0.1.zip Py-Previz
  adding: Py-Previz/ (stored 0%)
  adding: Py-Previz/Py-Previz.pyp (deflated 74%)
  adding: Py-Previz/res/ (stored 0%)
  adding: Py-Previz/res/lib/ (stored 0%)
  adding: Py-Previz/res/lib/python/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/previz/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/previz/__init__.py (deflated 74%)
```
