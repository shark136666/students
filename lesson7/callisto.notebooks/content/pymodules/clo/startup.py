import sys
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


def startup():
    """
    Inserting path to python modules for jupyter into PATH variable.
    """
    sys.path.insert(0, os.path.join(_get_server_root(), 'pymodules'))

if __name__ == '__main__':
    startup()
