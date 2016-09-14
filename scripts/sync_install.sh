#!/bin/bash

rsync --archive --progress --human-readable Py-Previz $HOME/Library/Preferences/MAXON/CINEMA\ 4D\ R17_89538A46/plugins
rsync --archive --progress --human-readable /Users/charles/src/previz-exporters/previz/previz $HOME/Library/Preferences/MAXON/CINEMA\ 4D\ R17_89538A46/plugins/Py-Previz/res/lib/python/site-packages
