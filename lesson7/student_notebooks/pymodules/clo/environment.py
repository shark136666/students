import os
from notebook import notebookapp


def _get_server_info():
    """
    Function returns notebookapp.list_running_servers() item.

    {'base_url': '/',
     'hostname': '<hostname>',
     'notebook_dir': '<path/to/notebooks/root/dir>',
     'password': <bool>,
     'pid': <pid:number>,
     'port': <port:number>,
     'secure': <bool>,
     'token': <token:string>,
     'url': 'http://<hostname>:<port>/'}
    """
    parent_pid = os.getppid()
    server = None
    for item in notebookapp.list_running_servers():
        if item['pid'] == parent_pid:
            server = item
            break
    return server


def _get_server_root():
    return _get_server_info()['notebook_dir']


class Environment(object):
    """
    Class that allow getting specific application paths.

        CALLISTO_DIR = - path to callisto application
        CALLISTO_NB_DIR - path to jupyter notebook root directory
        CALLISTO_CONF_DIR - path to configuration directory
        CALLISTO_HOME_DIR - path to home directory
        CALLISTO_SETTINGS_DIR - path to settings directory

        CALLISTO_GIT_PATH - path to git application
        CALLISTO_GIT_REMOTE_URL - remote git repository url
        CALLISTO_GIT_REMOTE_BRANCH - remote git branch for tracking
    """
    CALLISTO_DIR = 'CALLISTO_DIR'
    CALLISTO_NB_DIR = 'CALLISTO_NB_DIR'
    CALLISTO_CONF_DIR = 'CALLISTO_CONF_DIR'
    CALLISTO_HOME_DIR = 'CALLISTO_HOME_DIR'
    CALLISTO_SETTINGS_DIR = 'CALLISTO_SETTINGS_DIR'

    CALLISTO_GIT_PATH = 'CALLISTO_GIT_PATH'
    CALLISTO_GIT_REMOTE_URL = 'CALLISTO_GIT_REMOTE_URL'
    CALLISTO_GIT_REMOTE_BRANCH = 'CALLISTO_GIT_REMOTE_BRANCH'

    def __init__(self):
        pass

    @staticmethod
    def app_dir():
        try:
            return os.environ[Environment.CALLISTO_DIR]
        except KeyError:
            return os.path.realpath(os.path.join(Environment.nb_dir(), '..'))

    @staticmethod
    def nb_dir():
        try:
            return os.environ[Environment.CALLISTO_NB_DIR]
        except KeyError:
            return _get_server_root()

    @staticmethod
    def config_dir():
        return os.environ.get(Environment.CALLISTO_CONF_DIR, (
            os.path.realpath(os.path.join(Environment.app_dir(), 'conf'))))

    @staticmethod
    def home_dir():
        return os.environ.get(Environment.CALLISTO_HOME_DIR, (
            os.path.realpath(os.path.join(Environment.config_dir(), 'home'))))

    @staticmethod
    def settings_dir():
        return os.environ.get(Environment.CALLISTO_SETTINGS_DIR, (
            os.path.realpath(os.path.join(Environment.home_dir(), (
                'settings')))))
