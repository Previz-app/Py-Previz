from distutils.core import Command
from distutils.dir_util import copy_tree, remove_tree
from distutils.filelist import FileList
import imp
import os
import os.path

from glob2 import glob


class bdist_cinema4d_plugin(Command):
    description = "Build Cinema4d plugin"
    user_options = [('include-modules=', None, 'Comma-separated list of modules to include with the addon')]
    sub_commands = (('build', lambda self: True),)

    def initialize_options(self):
        self.include_modules = []

    def finalize_options(self):
        if type(self.include_modules) is str and len(self.include_modules) > 0:
            self.include_modules = self.include_modules.split(',')

    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        addon_name = self.distribution.get_name()
        dist_dir = self.get_finalized_command('bdist').dist_dir
        archive_name = '{}-v{}'.format(addon_name, self.distribution.get_version())
        addon_archive = os.path.join(dist_dir, archive_name)
        build_lib = self.get_finalized_command('build').build_lib
        build_plugin = os.path.join(build_lib, addon_name)
        site_packages = os.path.join(build_plugin, 'res/lib/python/site-packages')

        self.copy_tree(addon_name, build_plugin)

        for name in self.include_modules:
            src = imp.find_module(name)[1]
            dst = os.path.join(site_packages, name)
            self.copy_tree(src, dst)

        for pyc in glob(os.path.join(build_plugin, '**/*.pyc')):
            self.announce('Deleting %s' % pyc)
            os.remove(pyc)

        self.make_archive(addon_archive, 'zip', build_lib, addon_name)
