from abc import ABC, abstractmethod
from traitlets import parse_notifier_name


class Update(ABC):
    def __init__(self):
        self._listeners = {}

    @abstractmethod
    def check_updates(self):
        pass

    @abstractmethod
    def update(self):
        pass

    def on(self, names, handler):
        """
        def handler(event, updater)
        event - dict
        updater - updater class instance
        event has field 'name'. Value ['check_result', 'update_result']

        {'name': 'check_result',
         'result': <True/False>,
         'error': <string>,
         'timestamp': <timestamp ISO8601>}
        {'name': 'update_result',
         'result': <True/False>,
         'error': <string>}}
        """
        names = parse_notifier_name(names)
        for n in names:
            self._listeners.setdefault(n, []).append(handler)

    def off(self, names, handler):
        names = parse_notifier_name(names)
        for n in names:
            try:
                if handler is None:
                    del self._listeners[n]
                else:
                    self._listeners[n].remove(handler)
            except KeyError:
                pass

    def _notify(self, event):
        listeners = self._listeners.get(event['name'], [])
        for item in listeners:
            item(event, self)
