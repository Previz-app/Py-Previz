Previz Cinema4D integration
===========================


Development
-----------

* Create and activate a virtual environment:
``` sh
$ pyvenv-3.5 env
$ source env/bin/activate
(env) $
```
* To use a locally cloned `previz-python-api` repository, `pip install` it as a linked / editable dependencies before installing the other dependencies:
```
(env) $ pip install -e /path/to/previz-python-wrapper
```
* Install the dependencies:
``` sh
(env) $ pip install -r requirements.txt
```
* Sync the plugin to the plugin folder of the Cinema4D installation. This requires `rsync` executable.
``` sh
python setup.py rsync_cinema4d_plugin --destination=JohnDoe-MacBook-Pro.local:/Users/john/Library/Preferences/MAXON/CINEMA4D/plugins
```


Release
-------

`setup.py` defines a `bdist_cinema4d_plugin` command that build an addon archive in the `dist` directory.

```sh
# Build from a clean virtual env
$ pyvenv-3.5 env
$ source env/bin/activate

# Install the dependencies
(env) $ pip install -r requirements.txt

# Run [bumpversion](https://github.com/peritus/bumpversion) to update release version
# This will add a new git tag and will commit the new version
# Version types are: major, minor, patch
(env) $ bumpversion patch

# Build the addon archive
(env) $ python setup.py bdist_cinema4d_plugin
(env) $ ls dist
