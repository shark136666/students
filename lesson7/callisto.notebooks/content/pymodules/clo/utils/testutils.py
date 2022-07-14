import configparser
# walk
import os


class DeviceInformation(object):
    def __init__(self, manufacturer, name, path, description=''):
        if not manufacturer:
            raise ValueError('Device manufacturer can\'t be empty')

        if not name:
            raise ValueError('Device name can\'t be empty')

        if not path:
            raise ValueError('Device config path can\'t be empty')

        self.manufacturer = manufacturer
        self.name = name
        self.description = description
        self.path = path


class TestInformation(object):
    def __init__(self, name, start, description='', path=''):
        if not name:
            raise ValueError('Test name can\'t be empty')

        if not start:
            raise ValueError('Test start propetry can\'t be empty')

        self.name = name
        self.description = description
        self.start = start
        self.path = path


def get_device_configs(directory):
    devices = []
    for item in os.listdir(directory):
        parent_dir = os.path.join(directory, item)
        entries = os.listdir(parent_dir)
        for entry in entries:
            file = os.path.join(parent_dir, entry)
            if not os.path.isfile(file) or entry != 'device.cfg':
                continue
            devices.append(file)
    return devices


def read_devices_info(path, encoding='utf8', onerror=None):
    devices = []

    config = configparser.ConfigParser()
    try:
        if len(config.read(path, encoding=encoding)) == 0:
            return devices
    except configparser.Error as e:
        if onerror is not None:
            onerror(e)
        return devices

    for section in config.sections():
        try:
            s = config[section]
            t = DeviceInformation(manufacturer=s.get('manufacturer'),
                                  name=s.get('name'),
                                  description=s.get('description',
                                                    fallback=''),
                                  path=path)
            devices.append(t)
        except ValueError as e:
            if onerror is not None:
                e.section = section
                onerror(e)
            else:
                continue
        except configparser.Error as e:
            if onerror is not None:
                onerror(e)
            else:
                continue

    return devices


def read_tests_info(path, encoding='utf8', onerror=None):
    """
    If optional arg 'onerror' is specified, it should be a function; it
    will be called with one argument, an exception instance. It can
    report the error to continue parsing, or raise the exception
    to abort the parsing.
    """
    tests = []

    config = configparser.ConfigParser()
    try:
        if len(config.read(path, encoding=encoding)) == 0:
            return tests
    except configparser.Error as e:
        if onerror is not None:
            onerror(e)
        return tests

    for section in config.sections():
        try:
            s = config[section]
            t = TestInformation(name=s.get('name'),
                                description=s.get('description',
                                                  fallback=''),
                                start=s.get('start'),
                                path=path)
            tests.append(t)
        except ValueError as e:
            if onerror is not None:
                e.section = section
                onerror(e)
            else:
                continue
        except configparser.Error as e:
            if onerror is not None:
                onerror(e)
            else:
                continue

    return tests


def collect_device_tests(path, encoding='utf8', onerror=None):
    tests = []
    for (dirpath, _, filenames) in os.walk(path):
        for f in filenames:
            if f != 'test.cfg':
                continue
            tests.extend(read_tests_info(os.path.join(dirpath, f),
                                         encoding=encoding,
                                         onerror=onerror))
    return tests
