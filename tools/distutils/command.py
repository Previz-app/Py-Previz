from distutils.core import Command
from distutils.dir_util import copy_tree, remove_tree
from distutils.errors import DistutilsArgError
from distutils.filelist import FileList
from distutils.spawn import spawn
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
        addon_name = self.distribution.get_name()
        dist_dir = self.get_finalized_command('bdist').dist_dir
        archive_name = '{}-v{}'.format(addon_name, self.distribution.get_version())
        addon_archive = os.path.join(dist_dir, archive_name)
        build_lib = self.get_finalized_command('build').build_lib
        build_plugin = os.path.join(build_lib, addon_name)
        site_packages = os.path.join(build_plugin, 'res/lib/python/site-packages')

        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        self.copy_tree(addon_name, build_plugin)

        for name in self.include_modules:
            src = imp.find_module(name)[1]
            dst = os.path.join(site_packages, name)
            self.copy_tree(src, dst)

        to_deletes = glob(os.path.join(build_plugin, '**/*.pyc'))
        to_deletes.extend(glob(os.path.join(build_plugin, '**/c4d_debug.txt')))
        for to_delete in to_deletes:
            self.announce('Deleting %s' % to_delete)
            os.remove(to_delete)

        self.make_archive(addon_archive, 'zip', build_lib, addon_name)

    def get_plugin_path(self):
        return os.path.join(
            self.get_finalized_command('build').build_lib,
            self.distribution.get_name()
        )


class rsync_cinema4d_plugin(Command):
    description = 'Rsync Cinema4d plugin'
    user_options = [('destination=', None, 'Remote folder to rsync the plugin to')]
    sub_commands = (('bdist_cinema4d_plugin', lambda self: True),)

    def initialize_options(self):
        self.destination = None

    def finalize_options(self):
        if type(self.destination) is not str or len(self.destination) == 0:
            raise DistutilsArgError, 'No rsync destination specified'

    def run(self):
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        src = self.get_finalized_command('bdist_cinema4d_plugin').get_plugin_path()
        dst = self.destination
        cmd = [
            'rsync',
            '--archive',
            '--progress',
            '--human-readable',
            '--delete',
            src,
            dst
        ]
        spawn(cmd)
