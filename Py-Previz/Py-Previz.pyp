import contextlib
import os
import os.path
import shelve
import sys
import tempfile
import time
import webbrowser

import c4d
from c4d import documents, gui, plugins, storage, threading

# Add locale module path
local_modules_path = os.path.join(os.path.dirname(__file__),
                                  'res',
                                  'lib',
                                  'python',
                                  'site-packages')
sys.path.insert(0, local_modules_path)

import previz

__author__ = 'Charles Flèche'
__website__ = 'https://dandelion-burdock.beanstalkapp.com/'
__email__ = 'charles.fleche@gmail.com'
__version__ = "0.0.7"

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

GROUP_BUTTONS  = next(ids)
EXPORT_BUTTON  = next(ids)
PUBLISH_BUTTON = next(ids)

MSG_PUBLISH_DONE = __plugin_id__

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
            PROJECT_REFRESH_BUTTON: self.OnProjectRefreshButtonPressed,
            PROJECT_NEW_BUTTON:     self.OnProjectNewButtonPressed,
            EXPORT_BUTTON:          self.OnExportButtonPressed,
            PUBLISH_BUTTON:         self.OnPublishButtonPressed
        }

    @property
    def previz_project(self):
        api_root = 'https://app.previz.co/api'
        api_token = self.GetString(API_TOKEN_EDIT)
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

        self.GroupBegin(id=GROUP_BUTTONS,
                        flags=c4d.BFH_SCALEFIT,
                        cols=2,
                        rows=1,
                        title='Actions',
                        groupflags=c4d.BORDER_NONE)

        self.AddButton(id=EXPORT_BUTTON,
                       flags=c4d.BFH_SCALEFIT | c4d.BFV_BOTTOM,
                       name='Export to file')

        self.AddButton(id=PUBLISH_BUTTON,
                       flags=c4d.BFH_SCALEFIT | c4d.BFV_BOTTOM,
                       name='Publish to Previz')

        self.RefreshUI()

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

    def CoreMessage(self, id, msg):
        if id != MSG_PUBLISH_DONE:
            return gui.GeDialog.CoreMessage(self, id, msg)

        print 'PrevizDialog.CoreMessage', id, id == __plugin_id__
        self.RefreshUI()
        return True

    def Command(self, id, msg):
        print 'PrevizDialog.Command', id, msg

        # Refresh the UI so the user has immediate feedback
        self.RefreshUI()

        # Execute command
        command = self.commands.get(id)
        if command is not None:
            command(msg)

        # If a command modify a field, no event are sent
        # Forcing UI refresh again here
        self.RefreshUI()

        return True

    def OnAPITokenChanged(self, msg):
        print 'PrevizDialog.OnAPITokenChanged'
        token = self.GetString(API_TOKEN_EDIT)
        self.settings[SETTINGS_API_TOKEN] = token

    def OnAPITokenButtonPressed(self, msg):
        print 'PrevizDialog.OnAPITokenButtonPressed', msg
        webbrowser.open('https://app.previz.co/settings#/api')

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

    def OnExportButtonPressed(self, msg):
        print 'PrevizDialog.OnExportButtonPressed', msg

        filepath = c4d.storage.SaveDialog(
            type=c4d.FILESELECTTYPE_SCENES,
            title="Export scene to Previz JSON",
            force_suffix="json"
        )

        if filepath is None:
            return

        with open(filepath, 'w') as fp:
            previz.export(BuildPrevizScene(), fp)

    def OnPublishButtonPressed(self, msg):
        print 'PrevizDialog.OnPublishButtonPressed', msg

        # Write JSON to disk
        scene = BuildPrevizScene()

        fp, path = tempfile.mkstemp(prefix='previz-',
                                    suffix='.json',
                                    text=True)
        fp = os.fdopen(fp)
        previz.export(scene, fp)
        fp.close()

        # Upload JSON to Previz in a thread
        api_root = 'https://app.previz.co/api'
        api_token = self.GetString(API_TOKEN_EDIT)
        project_id = self.GetInt32(PROJECT_SELECT)

        global publisher_thread
        publisher_thread = PublisherThread(api_root, api_token, project_id, path)
        publisher_thread.Start()

        # Notice user of success

    def RefreshUI(self):
        self.RefreshProjectNewButton()
        self.RefreshPublishButton()

    def RefreshProjectNewButton(self):
        project_name = self.GetString(PROJECT_NEW_EDIT)
        project_name_is_valid = len(project_name) > 0
        self.Enable(PROJECT_NEW_BUTTON, project_name_is_valid)

    def RefreshPublishButton(self):
        print 'PrevizDialog.RefreshPublishButton'

        # Token
        api_token = self.GetString(API_TOKEN_EDIT)
        is_api_token_valid = len(api_token) > 0

        # Project
        project_id = self.GetInt32(PROJECT_SELECT)
        is_project_id_valid = project_id > 1

        # Publisher is running
        is_publisher_thread_running = publisher_thread is not None and publisher_thread.IsRunning()

        # Enable / Disable
        self.Enable(PUBLISH_BUTTON,
                    is_api_token_valid \
                    and is_project_id_valid \
                    and not is_publisher_thread_running)


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


################################################################################

def vertex_names(polygon):
    ret = ['a', 'b', 'c']
    if not polygon.IsTriangle():
        ret.append('d')
    return ret

def face_type(polygon, has_uvsets):
    """
    See https://github.com/mrdoob/three.js/wiki/JSON-Model-format-3
    """
    is_quad = not polygon.IsTriangle()
    return (int(is_quad) << 0) + (int(has_uvsets) << 3 )

def uvw_tags(obj):
    return list(t for t in obj.GetTags() if t.GetType() == c4d.Tuvw)

def parse_faces(obj):
    faces = []

    uvtags = uvw_tags(obj)
    has_uvsets = len(uvtags) > 0
    uvsets = [previz.UVSet(uvtag.GetName(), []) for uvtag in uvtags]

    for polygon_index, p in enumerate(obj.GetAllPolygons()):
        three_js_face_type = face_type(p, has_uvsets)
        faces.append(three_js_face_type)

        vertex_indices = list(getattr(p, vn) for vn in vertex_names(p))
        faces.append(vertex_indices)

        for uvtag, uvset in zip(uvtags, uvsets):
            uvdict = uvtag.GetSlow(polygon_index)
            for vn in vertex_names(p):
                uv = list((uvdict[vn].x, 1-uvdict[vn].y))
                uvset.coordinates.append(uv)
                faces.append(len(uvset)-1)

    return faces, uvsets

def get_vertices(obj):
    for v in obj.GetAllPoints():
		yield v

def parse_geometry(obj):
    vertices = ((v.x, v.y, v.z) for v in get_vertices(obj))

    uvtags = list(uvw_tags(obj))
    uvsets = [[] for i in range(len(uvtags))]

    faces, uvsets = parse_faces(obj)

    return obj.GetName() + 'Geometry', faces, vertices, uvsets

def serialize_matrix(m):
    yield m.v1.x
    yield m.v1.y
    yield m.v1.z
    yield 0

    yield m.v2.x
    yield m.v2.y
    yield m.v2.z
    yield 0

    yield m.v3.x
    yield m.v3.y
    yield m.v3.z
    yield 0

    yield m.off.x
    yield m.off.y
    yield m.off.z
    yield 1

AXIS_CONVERSION = c4d.utils.MatrixScale(c4d.Vector(1, 1, -1))

def convert_matrix(matrix):
    return serialize_matrix(AXIS_CONVERSION * matrix)

def parse_mesh(obj):
    name = obj.GetName()
    world_matrix = convert_matrix(obj.GetMg())
    geometry_name, faces, vertices, uvsets = parse_geometry(obj)

    return previz.Mesh(name,
                       geometry_name,
                       world_matrix,
                       faces,
                       vertices,
                       uvsets)

def iterate(obj):
    down = obj.GetDown()
    if down is not None:
        for o in iterate(down):
            yield o

    yield obj

    next = obj.GetNext()
    if next is not None:
        for o in iterate(next):
            yield o

def traverse(doc):
	objs = doc.GetObjects()
	if len(objs) == 0:
		return []
	return iterate(objs[0])

def exportable_objects(doc):
    return (o for o in traverse(doc) if isinstance(o, c4d.PolygonObject))

def build_objects(doc):
    for o in exportable_objects(doc):
        yield parse_mesh(o)

def BuildPrevizScene():
    print '---- START', 'BuildPrevizScene'
    print 'AXIS_CONVERSION'
    print AXIS_CONVERSION

    doc = c4d.documents.GetActiveDocument()
    doc = doc.Polygonize()

    return previz.Scene('Cinema4D-Previz',
                        os.path.basename(doc.GetDocumentPath()),
                        None,
                        build_objects(doc))

    print '---- END', 'BuildPrevizScene'


class PublisherThread(threading.C4DThread):
    def __init__(self, api_root, api_token, project_id, path):
        self.api_root = api_root
        self.api_token = api_token
        self.project_id = project_id
        self.path = path

    def Main(self):
        p = previz.PrevizProject(self.api_root,
                                 self.api_token,
                                 self.project_id)
        with open(self.path, 'rb') as fp:
            print 'START upload'
            p.update_scene(fp)
            print 'STOP upload'
        c4d.SpecialEventAdd(MSG_PUBLISH_DONE)

publisher_thread = None

def make_callback(text):
    def func(data):
        print text
    return func

plugin_messages = {
    c4d.C4DPL_STARTACTIVITY:       make_callback('C4DPL_STARTACTIVITY'),
    c4d.C4DPL_ENDACTIVITY:         make_callback('C4DPL_ENDACTIVITY'),
    c4d.C4DPL_RELOADPYTHONPLUGINS: make_callback('C4DPL_RELOADPYTHONPLUGINS'),
    c4d.C4DPL_COMMANDLINEARGS:     make_callback('C4DPL_COMMANDLINEARGS'),
    c4d.C4DPL_BUILDMENU:           make_callback('C4DPL_BUILDMENU'),
    c4d.C4DPL_ENDPROGRAM:          make_callback('C4DPL_ENDPROGRAM'),
    c4d.C4DPL_PROGRAM_STARTED:     make_callback('C4DPL_PROGRAM_STARTED')
}


def PluginMessage(id, data):
    cb = plugin_messages.get(id)
    print 'PluginMessage', id, data, cb
    if cb is None:
        return False
    cb(data)
    return True

if __name__ == '__main__':
    print 'Registering PrevizCommandData'
    plugins.RegisterCommandPlugin(id=__plugin_id__,
                                  str='Py-Previz',
                                  help='Py - Previz',
                                  info=0,
                                  dat=PrevizCommandData(),
                                  icon=None)
