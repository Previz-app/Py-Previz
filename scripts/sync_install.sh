#!/bin/bash

REPO_SRC=/home/charles/src/github/Previz-app
PLUGIN_SRC=$REPO_SRC/Py-Previz/Py-Previz
PREVIZ_MODULE_SRC=$REPO_SRC/previz-python-api/previz
REQUESTS_SRC=$REPO_SRC/Py-Previz/third-party/requests
REQUESTS_TOOLBELT_SRC=$REPO_SRC/Py-Previz/third-party/requests_toolbelt
SEMANTIC_VERSION_SRC=$REPO_SRC/Py-Previz/third-party/semantic_version

PLUGIN_DST='Nialls-MacBook-Pro.local:/Users/charles/Library/Preferences/MAXON/CINEMA4D/plugins/Py-Previz'
DEPS_DST=$PLUGIN_DST/res/lib/python/site-packages

rsync --archive --progress --human-readable --delete "$PLUGIN_SRC/" "$PLUGIN_DST"

rsync --archive --progress --human-readable \
    $PREVIZ_MODULE_SRC \
    $REQUESTS_SRC \
    $REQUESTS_TOOLBELT_SRC \
    $SEMANTIC_VERSION_SRC \
    $DEPS_DST
