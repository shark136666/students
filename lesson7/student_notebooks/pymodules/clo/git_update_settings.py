from clo.settings import Settings
from clo.environment import Environment
import os


class GitUpdateSettings(Settings):
    def __init__(self, root_dir=None):
        super().__init__(root_dir, prefix='update/git')

    def url(self):
        return super().value('url', os.environ.get(
            Environment.CALLISTO_GIT_REMOTE_URL,
            'ssh://git@altssh.bitbucket.org:443/planarllc/callisto.git'))

    def branch(self):
        return super().value('branch', os.environ.get(
            Environment.CALLISTO_GIT_REMOTE_BRANCH,
            'master'))

    def git_path(self):
        return super().value('git_path', os.environ.get(
            Environment.CALLISTO_GIT_PATH, os.path.realpath(os.path.join(
                Environment.app_dir(), 'git/cmd'))))
