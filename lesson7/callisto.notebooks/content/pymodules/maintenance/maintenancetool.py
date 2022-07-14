import subprocess
import os
from lxml import etree
from enum import IntEnum


class Maintenancetool(object):
    class ProxySettings(object):
        class Type(IntEnum):
            NO_PROXY = 0
            SYSTEM_PROXY = 1
            MANUAL_PROXY = 2

        def __init__(self, proxy_type, proxy=None):
            """
            :param proxy_type: value from class Type
            :param proxy: dictionary. See set() method for details
            """
            super().__init__()
            self.proxy_type = self.Type.NO_PROXY

            self.host = ''
            self.port = 80
            self.user = ''
            self.password = ''

            self.set(proxy_type, proxy)

        def set(self, proxy_type, proxy):
            """
            Settings up proxy
            :param proxy_type: value from class Type
            :param proxy: dictionery with keys:
                ['host', 'port', 'user', 'password']
            :return: None
            """
            self.proxy_type = proxy_type

            self.host = proxy.get('host', self.host)
            self.port = proxy.get('port', self.port)
            self.user = proxy.get('user', self.user)
            self.password = proxy.get('password', self.password)

    def __init__(self, tool_dir, name=None):
        """
        Class-wrapper for qt maintenance tool
        :param tool_dir: tool location directory
        :param name: maintenance file name (default: maintenancetool.exe)
        """
        super().__init__()
        self.tool_dir = tool_dir
        self.tool_name = name
        if self.tool_name is None:
            self.tool_name = 'maintenancetool.exe'

    def configure_proxy(self, proxy_settings):
        """
        Setting up proxy settings for maintenance tool in the network.xml file
        :param proxy_settings: ProxySettings class instance
        :return: None
        """
        network_path = os.path.join(self.tool_dir, 'network.xml')

        tree = etree.parse(network_path)

        # Network node
        root_node = tree.getroot()
        root_node.find('ProxyType').text = proxy_settings.proxy_type
        http_node = root_node.find('Http')
        http_node.find('Host').text = proxy_settings.host
        http_node.find('Port').text = str(proxy_settings.port)
        http_node.find('Username').text = proxy_settings.user
        http_node.find('Password').text = proxy_settings.password

        tree.write(network_path, xml_declaration=True, encoding='utf-8')

    def check_updates(self):
        """
        Perform check for updates
        :return: result (boolean), elementary tree-like object
        """
        updates_filepath = os.path.join(self.tool_dir, 'updates.xml')
        try:
            os.remove(updates_filepath)
        except:
            pass

        maintenance_path = os.path.join(self.tool_dir, self.tool_name)

        subprocess.run(args=[maintenance_path,
                             '--no-proxy',
                             '--checkupdates',
                             '>{}'.format(updates_filepath)],
                       shell=True,
                       check=True,
                       timeout=300)

        tree = etree.parse(updates_filepath)
        updates_node = tree.getroot()
        update_items = updates_node.findall('update')
        return len(update_items) > 0, etree.tostring(tree).decode('utf-8')

    def run_updater(self):
        """
        Execute maintenance tool in the updater mode (detached)
        :return: None
        """
        maintenance_path = os.path.join(self.tool_dir, self.tool_name)
        subprocess.Popen(args=[maintenance_path,
                               '--no-proxy',
                               '--updater'],
                         shell=True,
                         stdin=None,
                         stdout=None,
                         stderr=None,
                         close_fds=True)
