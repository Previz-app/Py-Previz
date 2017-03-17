Previz Cinema4D integration
===========================


Testing
-------

Unittesting is made with [tox](https://tox.readthedocs.io/en/latest/). Make sure the `blender` executable is in your `PATH`.


Development
-----------

Run something similar to `scripts/sync_install.sh` before reloading the plugin in Cinema4D.


Release
-------

Copy the `previz` and `requests` module into `Py-Previz/res/lib/python/site-packages` and zip the `Py-Previz` folder. Make sure that no stray __pycache__ files lying around. On Linux:

```sh
$ cd /path/to/repo
$ git clean -f -d -X
$ cd cinema4d
$ mkdir -p Py-Previz/res/lib/python/site-packages
$ cp -r ../previz/previz third-party/requests Py-Previz/res/lib/python/site-packages
$ grep __version__ Py-Previz/Py-Previz.pyp
__version__ = "0.0.2"
$ zip -r Py-Previz-v0.0.2.zip Py-Previz
  adding: Py-Previz/ (stored 0%)
  adding: Py-Previz/Py-Previz.pyp (deflated 74%)
  adding: Py-Previz/res/ (stored 0%)
  adding: Py-Previz/res/lib/ (stored 0%)
  adding: Py-Previz/res/lib/python/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/requests/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/requests/auth.py (deflated 71%)
  adding: Py-Previz/res/lib/python/site-packages/requests/utils.py (deflated 67%)
  adding: Py-Previz/res/lib/python/site-packages/requests/cookies.py (deflated 73%)
  adding: Py-Previz/res/lib/python/site-packages/requests/api.py (deflated 75%)
  adding: Py-Previz/res/lib/python/site-packages/requests/compat.py (deflated 61%)
  adding: Py-Previz/res/lib/python/site-packages/requests/exceptions.py (deflated 66%)
  adding: Py-Previz/res/lib/python/site-packages/requests/hooks.py (deflated 51%)
  adding: Py-Previz/res/lib/python/site-packages/requests/certs.py (deflated 42%)
  adding: Py-Previz/res/lib/python/site-packages/requests/_internal_utils.py (deflated 47%)
  adding: Py-Previz/res/lib/python/site-packages/requests/adapters.py (deflated 75%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/filepost.py (deflated 63%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/contrib/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/contrib/ntlmpool.py (deflated 68%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/contrib/pyopenssl.py (deflated 69%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/contrib/__init__.py (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/contrib/socks.py (deflated 70%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/contrib/appengine.py (deflated 70%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/response.py (deflated 72%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/connectionpool.py (deflated 72%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/connection.py (deflated 68%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/exceptions.py (deflated 68%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/packages/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/packages/six.py (deflated 75%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/packages/ordered_dict.py (deflated 69%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/packages/backports/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/packages/backports/makefile.py (deflated 60%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/packages/backports/__init__.py (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/packages/ssl_match_hostname/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/packages/ssl_match_hostname/__init__.py (deflated 52%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/packages/ssl_match_hostname/_implementation.py (deflated 59%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/packages/ssl_match_hostname/.gitignore (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/packages/__init__.py (deflated 27%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/poolmanager.py (deflated 70%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/request.py (deflated 68%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/__init__.py (deflated 60%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/fields.py (deflated 69%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/util/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/util/ssl_.py (deflated 66%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/util/response.py (deflated 57%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/util/connection.py (deflated 61%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/util/retry.py (deflated 69%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/util/request.py (deflated 66%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/util/__init__.py (deflated 58%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/util/url.py (deflated 65%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/util/timeout.py (deflated 70%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/urllib3/_collections.py (deflated 69%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/charsetgroupprober.py (deflated 70%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/escsm.py (deflated 81%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/jisfreq.py (deflated 53%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/sjisprober.py (deflated 66%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/big5prober.py (deflated 53%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/eucjpprober.py (deflated 65%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/jpcntx.py (deflated 74%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/mbcsgroupprober.py (deflated 56%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/cp949prober.py (deflated 53%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/compat.py (deflated 49%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/big5freq.py (deflated 54%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/sbcsgroupprober.py (deflated 68%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/langgreekmodel.py (deflated 81%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/universaldetector.py (deflated 73%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/sbcharsetprober.py (deflated 65%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/utf8prober.py (deflated 60%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/codingstatemachine.py (deflated 57%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/chardistribution.py (deflated 75%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/langthaimodel.py (deflated 75%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/euckrprober.py (deflated 53%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/langhebrewmodel.py (deflated 78%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/charsetprober.py (deflated 55%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/mbcharsetprober.py (deflated 64%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/euckrfreq.py (deflated 53%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/euctwprober.py (deflated 53%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/langbulgarianmodel.py (deflated 78%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/__init__.py (deflated 50%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/chardetect.py (deflated 57%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/gb2312freq.py (deflated 52%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/constants.py (deflated 48%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/langcyrillicmodel.py (deflated 83%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/latin1prober.py (deflated 68%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/escprober.py (deflated 64%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/langhungarianmodel.py (deflated 78%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/gb2312prober.py (deflated 53%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/hebrewprober.py (deflated 65%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/euctwfreq.py (deflated 52%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/chardet/mbcssm.py (deflated 84%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/README.rst (deflated 48%)
  adding: Py-Previz/res/lib/python/site-packages/requests/packages/__init__.py (deflated 50%)
  adding: Py-Previz/res/lib/python/site-packages/requests/sessions.py (deflated 72%)
  adding: Py-Previz/res/lib/python/site-packages/requests/cacert.pem (deflated 47%)
  adding: Py-Previz/res/lib/python/site-packages/requests/__init__.py (deflated 52%)
  adding: Py-Previz/res/lib/python/site-packages/requests/status_codes.py (deflated 62%)
  adding: Py-Previz/res/lib/python/site-packages/requests/structures.py (deflated 62%)
  adding: Py-Previz/res/lib/python/site-packages/requests/models.py (deflated 71%)
  adding: Py-Previz/res/lib/python/site-packages/previz/ (stored 0%)
  adding: Py-Previz/res/lib/python/site-packages/previz/__init__.py (deflated 74%)
```
