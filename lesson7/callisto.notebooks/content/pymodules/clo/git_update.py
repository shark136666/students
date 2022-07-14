from clo.update import Update
import subprocess
import threading
from jp.apputils import run_in_main_thread
from dataclasses import dataclass, field
import os
import re
from collections import namedtuple


def ssh_conf_is_proxy_command(line):
    """
    Function returns True if line is proxy command instruction.
    Othervise it returns False.
    """
    return bool(re.match(r'^\s*ProxyCommand', line, re.IGNORECASE))


def ssh_conf_parse_proxy(proxy_command):
    """
    Function returns dictionary with ssh proxy settings.
    Dictionary contains fields:
    'command' - proxy application
    'type' - proxy type
    'url' - proxy url
    'port' - proxy port

    If proxy settings isn't present, function returns empty dictionary.
    """
    template = (r'^\s*ProxyCommand'
                '\s\"?([^"]+)\"?'
                '\s+-(.)'
                '\s+?([^:]+):(\d+)'
                '\s+%h\s+%p\s*$')
    result = re.findall(template, proxy_command, re.IGNORECASE)
    # return result
    if len(result) != 1 or len(result[0]) != 4:
        return {}
    result = result[0]
    return {'command': result[0],
            'type': result[1],
            'url': result[2],
            'port': result[3]}


def ssh_conf_create_proxy_command(proxy):
    """
    Function creates proxy command string for ssh config file.
    proxy - dictionary with fields:
    'command' - proxy application
    'type' - proxy type
    'url' - proxy url
    'port' - proxy port
    """
    template = 'ProxyCommand {command} -{type} {url}:{port} %h %p'
    return template.format(command=proxy['command'],
                           type=proxy['type'],
                           url=proxy['url'],
                           port=proxy['port'])


@dataclass
class GitUpdate(Update):
    @staticmethod
    def _get_default_proxy():
        return {'type': '',
                'url': '',
                'port': '',
                'user': '',
                'passwd': ''}

    repo_path: str = ''
    repo_branch: str = 'master'
    remote_url: str = None
    git_path: str = None
    git_home: str = None
    proxy: dict = field(default_factory=_get_default_proxy.__func__)

    def __post_init__(self):
        # called after class initialization
        super().__init__()

    def check_updates(self):
        if hasattr(self, '_check_updates_thread'):
            return

        @run_in_main_thread
        def callback(event):
            if hasattr(self, '_check_updates_thread'):
                del self._check_updates_thread
            self._notify(event)

        env = self._create_env()
        try:
            GitUpdate._configure_connection(env, self.proxy)
        except Exception as e:
            callback({'name': 'check_result',
                      'result': False,
                      'error': str(e),
                      'timestamp': ''})
            return

        self._check_updates_thread = \
            threading.Thread(target=self._check_updates_impl,
                             args=(self._create_repo_data(), env, callback))
        self._check_updates_thread.start()

    def update(self):
        if hasattr(self, '_update_thread'):
            return

        @run_in_main_thread
        def callback(event):
            if hasattr(self, '_update_thread'):
                del self._update_thread
            self._notify(event)

        env = self._create_env()
        try:
            GitUpdate._configure_connection(env, self.proxy)
        except Exception as e:
            callback({'name': 'update_result',
                      'result': False,
                      'error': str(e)})
            return

        self._update_thread = \
            threading.Thread(target=self._update_impl,
                             args=(self._create_repo_data(), env, callback))
        self._update_thread.start()

    def _create_env(self):
        env = os.environ.copy()

        env['GIT_DIR'] = os.path.realpath(
            os.path.abspath(os.path.join(self.repo_path, '.git')))
        env['GIT_WORK_TREE'] = os.path.realpath(self.repo_path)

        if self.git_path is not None:
            env['PATH'] = (self.git_path +
                           os.pathsep +
                           # connect.exe
                           os.path.realpath(os.path.join(self.git_path,
                                                         '../mingw32/bin')) +
                           os.pathsep +
                           # ssh.exe
                           os.path.realpath(os.path.join(self.git_path,
                                                         '../usr/bin')) +
                           os.pathsep +
                           # add original PATH value
                           env.get('PATH', ''))

        if self.git_home is not None:
            env['HOME'] = self.git_home

        env['HTTP_PROXY_USER'] = self.proxy.get('user', '')
        env['HTTP_PROXY_PASSWORD'] = self.proxy.get('passwd', '')

        return env

    def _create_repo_data(self):
        return {'path': self.repo_path,
                'branch': self.repo_branch,
                'remote_url': self.remote_url,
                'remote_name': 'update',
                'remote_branch': self.repo_branch}

    @staticmethod
    def _configure_connection(environ, proxy):
        # Creating path to ssh config file.
        # Using environment variable with fallback to user profile location
        ssh_conf_path = os.path.realpath(os.path.join(
            environ.get('HOME', environ.get('USERPROFILE', '')),
            '.ssh/config'))

        # Config location checking
        if not os.path.exists(ssh_conf_path):
            dirname = os.path.dirname(ssh_conf_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            # create empty ssh config file
            with open(ssh_conf_path, 'w', encoding='utf-8') as f:
                f.write('')

        # Read config
        with open(ssh_conf_path, 'r', encoding='utf-8') as f:
            content = f.readlines()

        # Searching proxy parameter in the ssh config
        SearchResult = namedtuple('SearchResult', ['result', 'pos', 'proxy'])
        search_result = SearchResult(False, None, None)

        for i in range(len(content)):
            line = content[i]
            if not ssh_conf_is_proxy_command(line):
                continue

            proxy = ssh_conf_parse_proxy(line)
            search_result = SearchResult(True, i, proxy)

        # Handling search result
        update_ssh_cofig = True

        use_proxy = proxy.get('url', '') != ''

        if use_proxy:
            # creating proxy dictionary
            proxy['command'] = 'connect.exe'
            proxy['type'] = 'H'

            replace_proxy = False

            def proxy_command(proxy):
                return ssh_conf_create_proxy_command(proxy) + '\n'

            if search_result.result:
                keys = ('command', 'type', 'url', 'port')

                # comparing proxy objects
                for key in keys:
                    value1 = search_result.proxy.get(key, '').lower()
                    value2 = proxy.get(key, '').lower()
                    if value1 != value2:
                        replace_proxy = True

                if replace_proxy:
                    content[search_result.pos] = proxy_command(proxy)

                # if proxies are equal we don't need to rewrite config file
                update_ssh_cofig = replace_proxy
            else:
                # inserting proxy
                content.insert(0, proxy_command(proxy))
        else:
            if search_result.result:
                # delete proxy
                del content[search_result.pos]
            else:
                # do nothing
                update_ssh_cofig = False

        if update_ssh_cofig:
            with open(ssh_conf_path, 'w', encoding='utf-8') as f:
                f.write(''.join(content))

    @staticmethod
    def _bytes_to_unicode(bytes):
        return bytes.decode('cp866')

    @staticmethod
    def _clone_repo(env, remote_name, remote_url, repo_path, branch):
        env = env.copy()
        del env['GIT_DIR']
        del env['GIT_WORK_TREE']

        execute = ('git clone -o {remote_name} --single-branch '
                   '--branch {branch} {remote} \"{local}\"')
        GitUpdate._run_subprocess(execute.format(remote_name=remote_name,
                                                 branch=branch,
                                                 remote=remote_url,
                                                 local=repo_path),
                                  env)

    @staticmethod
    def _check_repo_remote(env, remote_name, remote_url, branch):
        """
        Checking repository remote configuration.
        """
        execute = 'git remote get-url {remote_name}'.format(
            remote_name=remote_name)
        sp_res = GitUpdate._run_subprocess(execute, env, check_rc=False)
        if sp_res.returncode != 0:
            # remote repository with name {remote_name} not found - creating it
            execute = ('git remote add -t {branch} -m {branch}'
                       ' {remote_name} {url}').format(branch=branch,
                                                      remote_name=remote_name,
                                                      url=remote_url)
            GitUpdate._run_subprocess(execute, env)

            execute = 'git remote update {remote_name}'.format(
                remote_name=remote_name)
            GitUpdate._run_subprocess(execute, env)
        else:
            # validating remote_url
            execute = 'git remote get-url {remote_name}'.format(
                remote_name=remote_name)
            sp_res = GitUpdate._run_subprocess(execute, env)
            url = GitUpdate._bytes_to_unicode(sp_res.stdout).strip()
            if url != remote_url:
                execute = 'git remote set-url {remote_name} {url}'.format(
                    remote_name=remote_name,
                    url=remote_url)
                GitUpdate._run_subprocess(execute, env)

        execute = ('git branch'
                   ' --set-upstream-to={remote_name}/{branch}'
                   ' {branch}').format(remote_name=remote_name,
                                       branch=branch)
        GitUpdate._run_subprocess(execute, env)

    @staticmethod
    def _prepare_repo(repo, env):
        repo_path = os.path.realpath(repo['path'])

        if not os.path.exists(os.path.join(repo_path, '.git')):
            try:
                os.makedirs(repo_path)
            except:
                pass

            GitUpdate._clone_repo(env=env,
                                  remote_name=repo['remote_name'],
                                  remote_url=repo['remote_url'],
                                  repo_path=repo_path,
                                  branch=repo['branch'])
        else:
            GitUpdate._check_repo_remote(env=env,
                                         remote_name=repo['remote_name'],
                                         remote_url=repo['remote_url'],
                                         branch=repo['branch'])

    @staticmethod
    def _run_subprocess(execute, env=None, check_rc=True, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = 60
        if 'shell' not in kwargs:
            kwargs['shell'] = True
        if 'capture_output' not in kwargs:
            kwargs['capture_output'] = True
        if kwargs.get('check', False):
            check_rc = False

        sp_res = subprocess.run(execute, env=env, **kwargs)
        if check_rc and sp_res.returncode != 0:
            msg = GitUpdate._bytes_to_unicode(sp_res.stderr).strip()
            msg += '\napp: {app}\nreturn code: {code}'.format(
                app=execute,
                code=sp_res.returncode)
            raise RuntimeError(msg)
        return sp_res

    @staticmethod
    def _check_updates_impl(repo, env, callback):
        result = {'name': 'check_result',
                  'result': False,
                  'error': 'Unknown error',
                  'timestamp': ''}

        try:
            GitUpdate._prepare_repo(repo, env)

            # updating local repo
            execute = 'git remote update {remote_name}'.format(
                remote_name=repo['remote_name'])
            GitUpdate._run_subprocess(execute, env)

            data = {}

            # getting commit hashes
            execute = 'git rev-parse {branch}'.format(branch=repo['branch'])
            sp_res = GitUpdate._run_subprocess(execute, env)
            data['local_hash'] = \
                GitUpdate._bytes_to_unicode(sp_res.stdout).strip()

            execute = 'git rev-parse {branch}@{{u}}'.format(
                branch=repo['branch'])
            sp_res = GitUpdate._run_subprocess(execute, env)
            data['remote_hash'] = \
                GitUpdate._bytes_to_unicode(sp_res.stdout).strip()

            execute = \
                'git merge-base {branch} {branch}@{{u}}'.format(
                    branch=repo['branch'])
            sp_res = GitUpdate._run_subprocess(execute, env)
            data['base_hash'] = \
                GitUpdate._bytes_to_unicode(sp_res.stdout).strip()

            """
            algorithm:
            # @ alone is a shortcut for HEAD.

            UPSTREAM=${1:-'@{u}'}
            LOCAL=$(git rev-parse @)
            REMOTE=$(git rev-parse "$UPSTREAM")
            BASE=$(git merge-base @ "$UPSTREAM")

            if [ $LOCAL = $REMOTE ]; then
                echo "Up-to-date"
            elif [ $LOCAL = $BASE ]; then
                echo "Need to pull"
            elif [ $REMOTE = $BASE ]; then
                echo "Need to push"
            else
                echo "Diverged"
            fi
            """
            if data['local_hash'] == data['remote_hash']:
                update_flag = False
            elif data['local_hash'] == data['base_hash']:
                update_flag = True
            else:
                raise RuntimeError('Invalid local repository')

            result['result'] = update_flag
            result['error'] = ''

            if update_flag:
                # date in ISO 8601 format
                execute = 'git show -s --format=%''cI {commit_hash}'.format(
                    commit_hash=data['remote_hash'])
                sp_res = GitUpdate._run_subprocess(execute, env)
                result['timestamp'] = \
                    GitUpdate._bytes_to_unicode(sp_res.stdout).strip()
        except Exception as e:
            result['error'] = str(e)

        callback(result)

    @staticmethod
    def _update_impl(repo, env, callback):
        result = {'name': 'update_result',
                  'result': False,
                  'error': 'Unknown error'}

        try:
            GitUpdate._prepare_repo(repo, env)

            GitUpdate._run_subprocess('git stash --all', env)

            execute = ('git checkout -B {branch}'
                       ' {remote_name}/{remote_branch}').format(
                       branch=repo['branch'],
                       remote_name=repo['remote_name'],
                       remote_branch=repo['branch'])
            GitUpdate._run_subprocess(execute, env)

            execute = 'git pull -r {origin} {branch}'.format(
                origin=repo['remote_name'],
                branch=repo['branch'])
            GitUpdate._run_subprocess(execute, env)

            result['result'] = True
            result['error'] = ''
        except Exception as e:
            result['error'] = str(e)

        callback(result)
