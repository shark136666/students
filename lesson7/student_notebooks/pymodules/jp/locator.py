import os
from notebook import notebookapp


def _normalize_path(path):
    return os.path.normcase(os.path.normpath(path)).replace('\\', '/')


def _get_server_info():
    parent_pid = os.getppid()
    server = None
    for item in notebookapp.list_running_servers():
        if item['pid'] == parent_pid:
            server = item
            break

    return server


def file_url(path, mode='apps'):
    server = _get_server_info()
    # ToDo server may be None. Check it!
    url = server['url']
    root_dir = _normalize_path(server['notebook_dir'])

    if not os.path.isabs(path):
        path = os.path.abspath(path)

    path = _normalize_path(path)
    common_path = os.path.commonprefix([root_dir, path])

    if common_path != root_dir:
    #     ToDo inform user
        return 'file_not_found.html'

    relpath = _normalize_path(os.path.relpath(path, root_dir))

    target_url = '{base_url}{mode}/{path}'.format(base_url=url,
                                                  mode=mode,
                                                  path=relpath)
    return target_url
