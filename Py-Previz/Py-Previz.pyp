import contextlib
import os
import os.path
import shelve
import sys
import tempfile
import time
import urlparse
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

__author__ = 'Previz'
__website__ = 'https://app.previz.co'
__email__ = 'info@previz.co'
__version__ = '1.0.2'

__plugin_id__ = 938453
__plugin_title__ = 'Previz'

DEFAULT_API_ROOT = __website__ + '/api'
DEFAULT_API_TOKEN = ''

def ids_iterator():
    for i in xrange(sys.maxint):
        yield i

ids=ids_iterator()

API_ROOT_LABEL = next(ids)
API_ROOT_EDIT  = next(ids)

API_TOKEN_LABEL  = next(ids)
API_TOKEN_EDIT   = next(ids)
API_TOKEN_BUTTON = next(ids)

TEAM_LABEL     = next(ids)
TEAM_SELECT    = next(ids)
PROJECT_LABEL  = next(ids)
PROJECT_SELECT = next(ids)
SCENE_LABEL    = next(ids)
SCENE_SELECT   = next(ids)

PROJECT_NEW_EDIT   = next(ids)
PROJECT_NEW_BUTTON = next(ids)
SCENE_NEW_EDIT     = next(ids)
SCENE_NEW_BUTTON   = next(ids)

REFRESH_BUTTON = next(ids)
EXPORT_BUTTON  = next(ids)
PUBLISH_BUTTON = next(ids)
NEW_VERSION_BUTTON = next(ids)

MSG_PUBLISH_DONE = __plugin_id__

SETTINGS_API_ROOT  = 'api_root'
SETTINGS_API_TOKEN = 'api_token'

debug_canary_path = os.path.join(os.path.dirname(__file__), 'c4d_debug.txt')

debug = os.path.exists(debug_canary_path)
teams = {}
new_plugin_version = None

def key(x):
    key = 'title' if 'title' in x else 'name'
    return x[key]

def find_by_key(items, key_name, key_value):
    for item in items:
        if item[key_name] == key_value:
            return item

class Restore(object):
    def __init__(self, getter, setter, ui_id):
        self.getter = getter
        self.setter = setter
        self.ui_id  = ui_id

        self.__restore_is_needed = False

    def __call__(self, value):
        if self.__restore_is_needed:
            return
        self.__restore_is_needed = self.old_value == value

    def __enter__(self):
        self.old_value = self.getter(self.ui_id)
        return self

    def __exit__(self, type, value, traceback):
        if self.__restore_is_needed:
            self.setter(self.ui_id, self.old_value)

class Settings(object):
    def __init__(self, namespace):
        self.namespace = namespace

        self.init()

    def init(self):
        if not os.path.isdir(self.dirpath):
            os.mkdir(self.dirpath)

        with self.open('c') as shelf:
            if SETTINGS_API_ROOT not in shelf:
                shelf[SETTINGS_API_ROOT] = DEFAULT_API_ROOT
            if SETTINGS_API_TOKEN not in shelf:
                shelf[SETTINGS_API_TOKEN] = DEFAULT_API_TOKEN

    def __getitem__(self, key):
        with self.open('r') as shelf:
            return shelf[key]

    def __setitem__(self, key, value):
        with self.open('w') as shelf:
            shelf[key] = value
            shelf.sync()

    def open(self, flag='r'):
        return contextlib.closing(shelve.open(self.path, flag))

    @property
    def path(self):
        return os.path.join(self.dirpath, 'settings')

    @property
    def dirpath(self):
        return os.path.join(storage.GeGetStartupWritePath(), self.namespace)


uuids = {}
def get_id_for_uuids(uuid):
    if uuid in uuids:
        return uuids[uuid]
    id = len(uuids)+1
    uuids[uuid] = id
    return id

def get_uuid_for_id(id_to_find):
    for uuid, id in uuids.items():
        if id_to_find == id:
            return uuid


def extract(data, next_name = None):
    ret = {
        'uuid': data['id'],
        'id': get_id_for_uuids(data['id']),
        'title': data['title']
    }
    if next_name is None:
        return ret

    ret[next_name] = []
    return ret, ret[next_name]


def extract_all(teams_data):
    teams = []
    for t in teams_data:
        team, projects = extract(t, 'projects')
        teams.append(team)
        for p in t['projects']:
            project, scenes = extract(p, 'scenes')
            projects.append(project)
            for s in p['scenes']:
                scene = extract(s)
                scenes.append(scene)
    return teams


class PrevizDialog(gui.GeDialog):
    def __init__(self):
        self.settings = Settings(__plugin_title__)

        self.commands = {
            API_ROOT_EDIT:      self.OnAPIRootChanged,
            API_TOKEN_EDIT:     self.OnAPITokenChanged,
            API_TOKEN_BUTTON:   self.OnAPITokenButtonPressed,
            TEAM_SELECT:        self.OnTeamSelectPressed,
            PROJECT_SELECT:     self.OnProjectSelectPressed,
            SCENE_SELECT:       self.OnSceneSelectPressed,
            PROJECT_NEW_BUTTON: self.OnProjectNewButtonPressed,
            SCENE_NEW_BUTTON:   self.OnSceneNewButtonPressed,
            REFRESH_BUTTON:     self.OnRefreshButtonPressed,
            EXPORT_BUTTON:      self.OnExportButtonPressed,
            PUBLISH_BUTTON:     self.OnPublishButtonPressed,
            NEW_VERSION_BUTTON: self.OnNewVersionButtonPressed
        }

    @property
    def previz_project(self):
        api_root = self.settings[SETTINGS_API_ROOT]
        api_token = self.settings[SETTINGS_API_TOKEN]

        global teams
        team = find_by_key(teams, 'id', self.GetInt32(TEAM_SELECT))
        projects = team['projects'] if team is not None else []
        project = find_by_key(projects, 'id', self.GetInt32(PROJECT_SELECT))
        project_uuid = project['uuid'] if project is not None else None

        return previz.PrevizProject(api_root, api_token, project_uuid)

    def get_all(self):
        return extract_all(self.previz_project.get_all())

    def refresh_all(self):
        global teams
        teams = self.get_all()
        self.RefreshTeamComboBox()

        global new_plugin_version
        new_plugin_version = self.previz_project.updated_plugin('cinema4d', __version__)
        self.RefreshNewVersionButton()

    def InitValues(self):
        print 'PrevizDialog.InitValues'

        self.SetString(API_ROOT_EDIT, self.settings[SETTINGS_API_ROOT])
        self.SetString(API_TOKEN_EDIT, self.settings[SETTINGS_API_TOKEN])

        self.RefreshUI()

        return True

    def CreateLayout(self):
        self.SetTitle(__plugin_title__)

        self.CreateAPIRootLine()

        self.CreateAPITokenLine()

        self.AddSeparatorH(1)

        self.GroupBegin(id=next(ids),
                        flags=c4d.BFH_SCALEFIT,
                        cols=2,
                        title='Previz',
                        groupflags=c4d.BORDER_NONE)

        self.CreateTeamLine()
        self.CreateProjectLine()
        self.CreateSceneLine()

        self.GroupEnd()

        self.AddSeparatorH(1)

        self.GroupBegin(id=next(ids),
                        flags=c4d.BFH_SCALEFIT,
                        cols=2,
                        title='Previz',
                        groupflags=c4d.BORDER_NONE)

        self.CreateNewProjectLine()
        self.CreateNewSceneLine()

        self.GroupEnd()

        self.AddSeparatorH(1)

        self.GroupBegin(id=next(ids),
                        flags=c4d.BFH_SCALEFIT,
                        cols=3,
                        rows=1,
                        title='Actions',
                        groupflags=c4d.BORDER_NONE)

        self.AddButton(id=REFRESH_BUTTON,
                       flags=c4d.BFH_SCALEFIT | c4d.BFV_BOTTOM,
                       name='Refresh')

        self.AddButton(id=EXPORT_BUTTON,
                       flags=c4d.BFH_SCALEFIT | c4d.BFV_BOTTOM,
                       name='Export to file')

        self.AddButton(id=PUBLISH_BUTTON,
                       flags=c4d.BFH_SCALEFIT | c4d.BFV_BOTTOM,
                       name='Publish to Previz')

        self.GroupEnd()

        self.AddButton(id=NEW_VERSION_BUTTON,
                       flags=c4d.BFH_SCALEFIT | c4d.BFV_BOTTOM,
                       name='') # defined in RefreshNewVersionButton

        return True

    def CreateAPIRootLine(self):
        self.GroupBegin(id=next(ids),
                        flags=c4d.BFH_SCALEFIT,
                        cols=2,
                        rows=1,
                        title='Previz',
                        groupflags=c4d.BORDER_NONE)

        self.AddStaticText(id=API_ROOT_LABEL,
                           flags=c4d.BFH_LEFT,
                           name='API root')

        self.AddEditText(id=API_ROOT_EDIT,
                         flags=c4d.BFH_SCALEFIT)

        self.GroupEnd()

    def CreateAPITokenLine(self):
        self.GroupBegin(id=next(ids),
                        flags=c4d.BFH_SCALEFIT,
                        cols=3,
                        rows=1,
                        title='Previz',
                        groupflags=c4d.BORDER_NONE)

        self.AddStaticText(id=API_TOKEN_LABEL,
                           flags=c4d.BFH_LEFT,
                           name='API token')

        self.AddEditText(id=API_TOKEN_EDIT,
                         flags=c4d.BFH_SCALEFIT)

        self.AddButton(id=API_TOKEN_BUTTON,
                       flags=c4d.BFH_FIT,
                       name='Get a token')

        self.GroupEnd()

    def CreateTeamLine(self):
        self.AddStaticText(id=TEAM_LABEL,
                           flags=c4d.BFH_LEFT,
                           name='Team')

        self.AddComboBox(id=TEAM_SELECT,
                         flags=c4d.BFH_SCALEFIT)

    def CreateProjectLine(self):
        self.AddStaticText(id=PROJECT_LABEL,
                           flags=c4d.BFH_LEFT,
                           name='Project')

        self.AddComboBox(id=PROJECT_SELECT,
                         flags=c4d.BFH_SCALEFIT)

    def CreateSceneLine(self):
        self.AddStaticText(id=SCENE_LABEL,
                           flags=c4d.BFH_LEFT,
                           name='Scene')

        self.AddComboBox(id=SCENE_SELECT,
                         flags=c4d.BFH_SCALEFIT)

    def CreateNewProjectLine(self):
        self.AddEditText(id=PROJECT_NEW_EDIT,
                         flags=c4d.BFH_SCALEFIT)

        self.AddButton(id=PROJECT_NEW_BUTTON,
                       flags=c4d.BFH_FIT,
                       name='New project')

    def CreateNewSceneLine(self):
        self.AddEditText(id=SCENE_NEW_EDIT,
                         flags=c4d.BFH_SCALEFIT)

        self.AddButton(id=SCENE_NEW_BUTTON,
                       flags=c4d.BFH_FIT,
                       name='New scene')

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

    def OnAPIRootChanged(self, msg):
        print 'PrevizDialog.OnAPIRootChanged'
        api_root = self.GetString(API_ROOT_EDIT)
        self.settings[SETTINGS_API_ROOT] = api_root

    def OnAPITokenChanged(self, msg):
        print 'PrevizDialog.OnAPITokenChanged'
        token = self.GetString(API_TOKEN_EDIT)
        self.settings[SETTINGS_API_TOKEN] = token

    def OnAPITokenButtonPressed(self, msg):
        print 'PrevizDialog.OnAPITokenButtonPressed', msg
        api_root = self.settings[SETTINGS_API_ROOT]
        s = urlparse.urlsplit(api_root)
        url = urlparse.urlunsplit((s.scheme, s.netloc, '/account/api', '', ''))
        webbrowser.open(url)

    def OnTeamSelectPressed(self, msg):
        print 'PrevizDialog.OnTeamSelectPressed', msg
        self.RefreshTeamComboBox()

    def OnProjectSelectPressed(self, msg):
        print 'PrevizDialog.OnProjectSelectPressed', msg
        self.RefreshSceneComboBox()

    def OnSceneSelectPressed(self, msg):
        print 'PrevizDialog.OnSceneSelectPressed', msg

    def OnRefreshButtonPressed(self, msg):
        print 'PrevizDialog.OnRefreshButtonPressed', msg
        self.refresh_all()

    def set_default_id_if_needed(self, id, iterable):
        if self.GetInt32(id) == -1 and len(iterable) > 0:
            v = iterable[0]['id']
            self.SetInt32(id, v)

    def RefreshTeamComboBox(self):
        print 'PrevizDialog.RefreshTeamComboBox'

        with Restore(self.GetInt32, self.SetInt32, TEAM_SELECT) as touch:
            self.FreeChildren(TEAM_SELECT)

            global teams
            for team in sorted(teams, key=key):
                id   = team['id']
                name = team['title']
                self.AddChild(TEAM_SELECT, id, name)
                touch(id)

        self.set_default_id_if_needed(TEAM_SELECT, sorted(teams, key=key))

        self.LayoutChanged(TEAM_SELECT)

        print 'RefreshTeamComboBox', touch.old_value, self.GetInt32(TEAM_SELECT)
        self.RefreshProjectComboBox()

    def RefreshProjectComboBox(self):
        print 'PrevizDialog.RefreshProjectComboBox'

        with Restore(self.GetInt32, self.SetInt32, PROJECT_SELECT) as touch:
            self.FreeChildren(PROJECT_SELECT)

            global teams
            team     = find_by_key(teams, 'id', self.GetInt32(TEAM_SELECT))
            projects = [] if team is None else team['projects']

            for project in projects:
                id   = project['id']
                title = project['title']
                self.AddChild(PROJECT_SELECT, id, title)
                touch(id)

        self.set_default_id_if_needed(PROJECT_SELECT, sorted(projects, key=key))

        self.LayoutChanged(PROJECT_SELECT)

        self.RefreshSceneComboBox()

    def RefreshSceneComboBox(self):
        print 'PrevizDialog.RefreshSceneComboBox'

        with Restore(self.GetInt32, self.SetInt32, SCENE_SELECT) as touch:
            self.FreeChildren(SCENE_SELECT)

            global teams
            team     = find_by_key(teams, 'id', self.GetInt32(TEAM_SELECT))
            projects = [] if team is None else team['projects']
            project  = find_by_key(projects, 'id', self.GetInt32(PROJECT_SELECT))
            scenes   = [] if project is None else project['scenes']

            for scene in scenes:
                id = scene['id']
                name = scene['title']
                self.AddChild(SCENE_SELECT, id, name)
                touch(id)

        self.set_default_id_if_needed(SCENE_SELECT, sorted(scenes, key=key))

        self.LayoutChanged(SCENE_SELECT)

    def OnProjectNewButtonPressed(self, msg):
        print 'PrevizDialog.OnProjectNewButtonPressed', msg

        # New project
        global teams
        team_uuid = find_by_key(teams, 'id', self.GetInt32(TEAM_SELECT))['uuid']
        project_name = self.GetString(PROJECT_NEW_EDIT)
        project = self.previz_project.new_project(project_name, team_uuid)
        self.refresh_all()

        # Clear project name
        # For some reason SetString doesn't send an event

        self.SetString(PROJECT_NEW_EDIT, '')
        self.RefreshProjectNewButton()

        # Select new project

        self.RefreshProjectComboBox()

        project_uuid = project['id']
        team = find_by_key(teams, 'id', self.GetInt32(TEAM_SELECT))
        projects = team['projects']
        project = find_by_key(projects, 'uuid', project_uuid)
        self.SetInt32(PROJECT_SELECT, project['id'])

    def OnSceneNewButtonPressed(self, msg):
        print 'PrevizDialog.OnSceneNewButtonPressed', msg

        # New scene

        scene_name = self.GetString(SCENE_NEW_EDIT)
        scene = self.previz_project.new_scene(scene_name)
        self.refresh_all()

        # Clear scene name
        # For some reason SetString doesn't send an event

        self.SetString(SCENE_NEW_EDIT, '')
        self.RefreshSceneNewButton()

        # Select new scene

        self.RefreshSceneComboBox()

        scene_uuid = scene['id']
        global teams
        team = find_by_key(teams, 'id', self.GetInt32(TEAM_SELECT))
        project = find_by_key(team['projects'], 'id', self.GetInt32(PROJECT_SELECT))
        scene = find_by_key(project['scenes'], 'uuid', scene_uuid)
        self.SetInt32(SCENE_SELECT, scene['id'])

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
        fp = os.fdopen(fp, 'w')
        previz.export(scene, fp)
        fp.close()

        # Upload JSON to Previz in a thread
        api_root = self.settings[SETTINGS_API_ROOT]
        api_token = self.settings[SETTINGS_API_TOKEN]
        project_id = self.GetInt32(PROJECT_SELECT)
        scene_id = self.GetInt32(SCENE_SELECT)

        project_uuid = get_uuid_for_id(project_id)
        scene_uuid = get_uuid_for_id(scene_id)

        global publisher_thread
        publisher_thread = PublisherThread(api_root, api_token, project_uuid, scene_uuid, path)
        publisher_thread.Start()

        # Notify user of success

    def OnNewVersionButtonPressed(self, msg):
        print 'PrevizDialog.OnNewVersionButtonPressed', msg
        webbrowser.open(new_plugin_version['downloadUrl'])

    def RefreshUI(self):
        print 'PrevizDialog.RefreshUI'

        self.RefreshProjectNewButton()
        self.RefreshSceneNewButton()
        self.RefreshRefreshButton()
        self.RefreshPublishButton()
        self.RefreshNewVersionButton()

    def RefreshProjectNewButton(self):
        team_id = self.GetInt32(TEAM_SELECT)
        team_id_is_valid = team_id >= 1

        project_name = self.GetString(PROJECT_NEW_EDIT)
        project_name_is_valid = len(project_name) > 0

        self.Enable(PROJECT_NEW_BUTTON,
                    team_id_is_valid \
                    and project_name_is_valid)

    def RefreshSceneNewButton(self):
        project_id = self.GetInt32(PROJECT_SELECT)
        project_id_is_valid = project_id >= 1

        scene_name = self.GetString(SCENE_NEW_EDIT)
        scene_name_is_valid = len(scene_name) > 0

        self.Enable(SCENE_NEW_BUTTON,
                    project_id_is_valid \
                    and scene_name_is_valid)

    def RefreshRefreshButton(self):
        api_token = self.GetString(API_TOKEN_EDIT)
        is_api_token_valid = len(api_token) > 0
        self.Enable(REFRESH_BUTTON, is_api_token_valid)

    def RefreshPublishButton(self):
        # Token
        api_token = self.GetString(API_TOKEN_EDIT)
        is_api_token_valid = len(api_token) > 0

        # Team
        team_id = self.GetInt32(TEAM_SELECT)
        is_team_id_valid = team_id >= 1

        # Project
        project_id = self.GetInt32(PROJECT_SELECT)
        is_project_id_valid = project_id >= 1

        # Scene
        scene_id = self.GetInt32(SCENE_SELECT)
        is_scene_id_valid = scene_id >= 1

        # Publisher is running
        is_publisher_thread_running = publisher_thread is not None and publisher_thread.IsRunning()

        # Enable / Disable
        self.Enable(PUBLISH_BUTTON,
                    is_api_token_valid \
                    and is_team_id_valid \
                    and is_project_id_valid \
                    and is_scene_id_valid \
                    and not is_publisher_thread_running)

    def RefreshNewVersionButton(self):
        global new_plugin_version

        text = 'Previz v%s' % __version__
        enable = False
        if new_plugin_version is not None:
            text = 'Download v%s (installed: v%s)' % (new_plugin_version['version'], __version__)
            enable = True

        self.SetString(NEW_VERSION_BUTTON, text)
        self.Enable(NEW_VERSION_BUTTON, enable)


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

    uv_index = 0
    for polygon_index, p in enumerate(obj.GetAllPolygons()):
        three_js_face_type = face_type(p, has_uvsets)
        faces.append(three_js_face_type)

        vertex_indices = list(getattr(p, vn) for vn in vertex_names(p))
        faces.append(vertex_indices)

        uv_index_local = uv_index
        for uvtag, uvset in zip(uvtags, uvsets):
            uvdict = uvtag.GetSlow(polygon_index)
            uv_index_offset = 0
            for vn in vertex_names(p):
                uv = list((uvdict[vn].x, 1-uvdict[vn].y))
                uvset.coordinates.append(uv)
                cur_uv_index = uv_index_local + uv_index_offset
                faces.append(cur_uv_index)
                uv_index_offset += 1
        uv_index = cur_uv_index + 1

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

    doc = c4d.documents.GetActiveDocument()
    doc = doc.Polygonize()

    return previz.Scene('Cinema4D-Previz',
                        os.path.basename(doc.GetDocumentPath()),
                        None,
                        build_objects(doc))

    print '---- END', 'BuildPrevizScene'


class PublisherThread(threading.C4DThread):
    def __init__(self, api_root, api_token, project_uuid, scene_uuid, path):
        self.api_root = api_root
        self.api_token = api_token
        self.project_uuid = project_uuid
        self.scene_uuid = scene_uuid
        self.path = path

    def Main(self):
        p = previz.PrevizProject(self.api_root,
                                 self.api_token,
                                 self.project_uuid)
        scene = p.scene(self.scene_uuid, include=[])
        json_url = scene['jsonUrl']
        with open(self.path, 'rb') as fp:
            print 'START upload'
            p.update_scene(json_url, fp)
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
    if debug:
        print 'DEBUG MODE as this file exists:', debug_canary_path
    print 'Registering PrevizCommandData'
    plugins.RegisterCommandPlugin(id=__plugin_id__,
                                  str='Py-Previz',
                                  help='Py - Previz',
                                  info=0,
                                  dat=PrevizCommandData(),
                                  icon=None)
