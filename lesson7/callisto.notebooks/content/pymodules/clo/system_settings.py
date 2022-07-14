from clo.settings import Settings
from enum import IntEnum


class ProxyType(IntEnum):
    NO_PROXY = 0
    SYSTEM_PROXY = 1
    MANUAL_PROXY = 2


class SystemSettings(Settings):
    def __init__(self, root_dir=None):
        super().__init__(root_dir, prefix='system')

    def get_proxy_type(self):
        return super().value('proxy_type', int(ProxyType.NO_PROXY))

    def set_proxy_type(self, proxy_type):
        super().set_value('proxy_type', int(proxy_type))

    def get_proxy(self):
        return super().value('proxy',
                             {'host': '',
                              'port': '',
                              'user': '',
                              'password': ''})

    def set_proxy(self, proxy):
        super().set_value('proxy', proxy)

    def set_proxy_host(self, host):
        proxy = self.get_proxy()
        proxy['host'] = host
        self.set_proxy(proxy)

    def set_proxy_port(self, port):
        proxy = self.get_proxy()
        proxy['port'] = port
        self.set_proxy(proxy)

    def set_proxy_user(self, user):
        proxy = self.get_proxy()
        proxy['user'] = user
        self.set_proxy(proxy)

    def set_proxy_password(self, password):
        proxy = self.get_proxy()
        proxy['password'] = password
        self.set_proxy(proxy)
