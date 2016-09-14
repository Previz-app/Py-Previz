import contextlib
import os
import os.path
import shelve
import sys
import webbrowser

import c4d
from c4d import gui, plugins, storage

# Add locale module path
local_modules_path = os.path.join(os.path.dirname(__file__),
                                  'res',
                                  'lib',
                                  'python',
                                  'site-packages')
sys.path.insert(0, local_modules_path)

import previz

__plugin_id__ = 938453
__plugin_title__ = 'Previz'

def ids_iterator():
    for i in xrange(sys.maxint):
        yield i

ids=ids_iterator()

GROUP_GRID = next(ids)

API_TOKEN_LABEL  = next(ids)
API_TOKEN_EDIT   = next(ids)
API_TOKEN_BUTTON = next(ids)

PROJECT_LABEL          = next(ids)
PROJECT_SELECT         = next(ids)
PROJECT_REFRESH_BUTTON = next(ids)

PROJECT_NEW_LABEL  = next(ids)
PROJECT_NEW_EDIT   = next(ids)
PROJECT_NEW_BUTTON = next(ids)

PUBLISH_BUTTON = next(ids)

SETTINGS_API_TOKEN = 'api_token'

class Settings(object):
    def __init__(self, namespace):
        self.namespace = namespace

        self.init()

    def init(self):
        if not os.path.isdir(self.dirpath):
            os.mkdir(self.dirpath)

        with self.open('c') as shelf:
            if SETTINGS_API_TOKEN not in shelf:
                shelf[SETTINGS_API_TOKEN] = ''

    def __getitem__(self, key):
        with self.open('r') as shelf:
            return shelf[key]

    def __setitem__(self, key, value):
        with self.open('w') as shelf:
            shelf[key] = value
            shelf.sync()

    def open(self, flag='r'):
        print self.path
        return contextlib.closing(shelve.open(self.path, flag))

    @property
    def path(self):
        return os.path.join(self.dirpath, 'settings')

    @property
    def dirpath(self):
        return os.path.join(storage.GeGetStartupWritePath(), self.namespace)

class PrevizDialog(gui.GeDialog):
    def __init__(self):
        self.settings = Settings(__plugin_title__)

        self.commands = {
            API_TOKEN_EDIT:         self.OnAPITokenChanged,
            API_TOKEN_BUTTON:       self.OnAPITokenButtonPressed,
            PROJECT_SELECT:         self.OnProjectComboBoxChanged,
            PROJECT_REFRESH_BUTTON: self.OnProjectRefreshButtonPressed,
            PROJECT_NEW_EDIT:       self.OnProjectNewEditChanged,
            PROJECT_NEW_BUTTON:     self.OnProjectNewButtonPressed,
            PUBLISH_BUTTON:         self.OnPublishButtonPressed
        }

    @property
    def previz_project(self):
        api_root = 'https://previz.online/api'
        api_token = self.settings[SETTINGS_API_TOKEN]
        return previz.PrevizProject(api_root, api_token)

    def InitValues(self):
        print 'PrevizDialog.InitValues'

        self.SetString(API_TOKEN_EDIT, self.settings['api_token'])

        return True

    def CreateLayout(self):
        self.SetTitle(__plugin_title__)

        self.GroupBegin(id=GROUP_GRID,
                        flags=c4d.BFH_SCALEFIT,
                        cols=3,
                        rows=2,
                        title='Previz',
                        groupflags=c4d.BORDER_NONE)

        self.CreateAPITokenLine()
        self.CreateProjectLine()
        self.CreateNewProjectLine()

        self.GroupEnd()

        self.AddButton(id=PUBLISH_BUTTON,
                       flags=c4d.BFH_CENTER | c4d.BFV_BOTTOM,
                       name='Publish to Previz')

        return True

    def CreateAPITokenLine(self):
        self.AddStaticText(id=API_TOKEN_LABEL,
                           flags=c4d.BFH_LEFT,
                           name='API token')

        self.AddEditText(id=API_TOKEN_EDIT,
                         flags=c4d.BFH_SCALEFIT)

        self.AddButton(id=API_TOKEN_BUTTON,
                       flags=c4d.BFH_FIT,
                       name='Get a token')

    def CreateProjectLine(self):
        self.AddStaticText(id=PROJECT_LABEL,
                           flags=c4d.BFH_LEFT,
                           name='Project')

        self.AddComboBox(id=PROJECT_SELECT,
                         flags=c4d.BFH_SCALEFIT)

        self.AddButton(id=PROJECT_REFRESH_BUTTON,
                       flags=c4d.BFH_FIT,
                       name='Refresh')

    def CreateNewProjectLine(self):
        self.AddStaticText(id=PROJECT_NEW_LABEL,
                           flags=c4d.BFH_LEFT,
                           name='New project')

        self.AddEditText(id=PROJECT_NEW_EDIT,
                         flags=c4d.BFH_SCALEFIT)

        self.AddButton(id=PROJECT_NEW_BUTTON,
                       flags=c4d.BFH_FIT,
                       name='New')
        self.RefreshProjectNewButton()

    def CoreMessage(self, id, msg):
        if id != __plugin_id__:
            return gui.GeDialog.CoreMessage(self, id, msg)

        print 'PrevizDialog.CoreMessage', id, id == __plugin_id__
        return True

    def Command(self, id, msg):
        print 'PrevizDialog.Command', id, msg
        self.commands[id](msg)
        return True

    def OnAPITokenChanged(self, msg):
        print 'PrevizDialog.OnAPITokenChanged'
        token = self.GetString(API_TOKEN_EDIT)
        self.settings[SETTINGS_API_TOKEN] = token

    def OnAPITokenButtonPressed(self, msg):
        print 'PrevizDialog.OnAPITokenButtonPressed', msg
        webbrowser.open('https://previz.online/settings#/api')

    def OnProjectComboBoxChanged(self, msg):
        print 'PrevizDialog.OnProjectComboBoxChanged', msg

    def OnProjectRefreshButtonPressed(self, msg):
        print 'PrevizDialog.OnProjectRefreshButtonPressed', msg
        self.RefreshProjectComboBox()

    def RefreshProjectComboBox(self):
        projects = sorted(self.previz_project.projects(),
                          key= lambda x: x['title'])
        self.FreeChildren(PROJECT_SELECT)
        for project in projects:
            self.AddChild(PROJECT_SELECT,
                          project['id'],
                          project['title'])

    def OnProjectNewEditChanged(self, msg):
        print 'PrevizDialog.OnProjectNewEditChanged', msg
        self.RefreshProjectNewButton()

    def RefreshProjectNewButton(self):
        project_name = self.GetString(PROJECT_NEW_EDIT)
        project_name_is_valid = len(project_name) > 0
        self.Enable(PROJECT_NEW_BUTTON, project_name_is_valid)

    def OnProjectNewButtonPressed(self, msg):
        print 'PrevizDialog.OnProjectNewButtonPressed', msg

        # New project

        project_name = self.GetString(PROJECT_NEW_EDIT)
        project = self.previz_project.new_project(project_name)

        # Clear project name
        # For some reason SetString doesn't send an event

        self.SetString(PROJECT_NEW_EDIT, '')
        self.RefreshProjectNewButton()

        # Select new project

        self.RefreshProjectComboBox()
        self.SetInt32(PROJECT_SELECT, project['id'])

    def OnPublishButtonPressed(self, msg):
        print 'PrevizDialog.OnPublishButtonPressed', msg


class PrevizCommandData(plugins.CommandData):
    dialog = None

    def Execute(self, doc):
        self.init_dialog_if_needed()
        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC,
                                pluginid=__plugin_id__,
                                defaultw=250,
                                defaulth=50)

    def RestoreLayout(self, sec_ref):
        self.init_dialog_if_needed()
        return self.dialog.Restore(pluginid=__plugin_id__,
                                   secret=sec_ref)

    def Message(self, type, data):
        #print 'PrevizCommandData.Message', type, data
        return False

    def init_dialog_if_needed(self):
        if self.dialog is None:
            self.dialog = PrevizDialog()


if __name__ == '__main__':
    print 'Registering PrevizCommandData'
    plugins.RegisterCommandPlugin(id=__plugin_id__,
                                  str='Py-Previz',
                                  help='Py - Previz',
                                  info=0,
                                  dat=PrevizCommandData(),
                                  icon=None)
