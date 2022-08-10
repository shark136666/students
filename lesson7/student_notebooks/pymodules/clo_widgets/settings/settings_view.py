from abc import ABC, abstractmethod
from ipywidgets import widgets
from IPython.display import display
from clo.system_settings import SystemSettings
import os
import jp.widgetutils as widgetutils


class SettingsPage(ABC):
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def set_default(self):
        pass

    @abstractmethod
    def widget(self):
        pass


class ProxySettings(SettingsPage):
    def __init__(self, system_settings):
        """Construct ProxySettings widget.

        system_settings - SystemSettings class instance
        """
        super().__init__()
        self.settings_sys = system_settings
        proxy = self.settings_sys.get_proxy()

        self.ui_rb_proxy_type = widgets.RadioButtons(
            description='Proxy type:',
            options=['no proxy', 'system proxy', 'manual']
        )

        self.ui_rb_proxy_type.value = \
            self.ui_rb_proxy_type.options[self.settings_sys.get_proxy_type()]
        self.ui_rb_proxy_type.is_manual_type = \
            lambda: self.ui_rb_proxy_type.index == len(self.ui_rb_proxy_type.options) - 1
        self.ui_rb_proxy_type.observe(
            lambda change: self._proxy_type_changed(change))

        self.ui_host = widgets.Text(value=proxy.get('host', ''),
                                    placeholder='proxy server',
                                    description='HTTP proxy')
        port = 8080
        try:
            port = int(proxy.get('port', port))
        except ValueError:
            pass

        self.ui_port = widgets.BoundedIntText(value=port,
                                              min=1,
                                              max=65535,
                                              step=1,
                                              description='port')
        self.ui_user = widgets.Text(value=proxy.get('user', ''),
                                    placeholder='username',
                                    description='user')
        self.ui_password = widgets.Password(value=proxy.get('password', ''),
                                            placeholder='password',
                                            description='password')

        self.ui_proxy = widgets.VBox([self.ui_host,
                                      self.ui_port,
                                      self.ui_user,
                                      self.ui_password])

        self.ui_widget = widgets.VBox([self.ui_rb_proxy_type,
                                       self.ui_proxy])
        self._sync()

    def _sync(self):
        self._enable_proxy_editing(self.ui_rb_proxy_type.is_manual_type())

    def _proxy_type_changed(self, change):
        if change['name'] == 'value':
            self._enable_proxy_editing(self.ui_rb_proxy_type.is_manual_type())

    def _enable_proxy_editing(self, enable=True):
        for w in self.ui_proxy.children:
            widgetutils.enable_widget(w, enable)

    def _normalize(self):
        self.ui_host.value = self.ui_host.value.strip()
        self.ui_user.value = self.ui_user.value.strip()

    def _validate(self):
        self._normalize()

        if not self.ui_rb_proxy_type.is_manual_type():
            return

        if self.ui_host.value == '':
            raise ValueError('HTTP proxy url can\'t be empty.')

        if self.ui_user.value == '' and self.ui_password.value != '':
            raise ValueError(
                'HTTP proxy user can\'t be empty if proxy password provided.')

    def name(self):
        return 'Proxy'

    def save(self):
        self._validate()

        proxy_type = self.ui_rb_proxy_type.index
        self.settings_sys.set_proxy_type(proxy_type)

        if self.ui_rb_proxy_type.is_manual_type():
            proxy = {
                'host': self.ui_host.value,
                'port': self.ui_port.value,
                'user': self.ui_user.value,
                'password': self.ui_password.value,
            }
            self.settings_sys.set_proxy(proxy)

    def set_default(self):
        self.ui_rb_proxy_type.index = 0
        self.ui_host.value = ''
        self.ui_port.value = 8080
        self.ui_user.value = ''
        self.ui_password.value = ''

    def widget(self):
        return self.ui_widget


class SettingsView(object):
    def __init__(self, pages):
        super().__init__()
        self.pages = pages

        self.ui_tab = widgets.Tab()
        self.ui_tab.children = [c.widget() for c in self.pages]
        for i in range(len(self.pages)):
            self.ui_tab.set_title(i, self.pages[i].name())

        self.ui_btn_save = \
            widgets.Button(description='Save',
                           tooltip='Save settings')
        self.ui_btn_save.on_click(lambda btn: self._save_on_click(btn))

        self.ui_btn_cancel = \
            widgets.Button(description='Cancel',
                           tooltip='Exit without saving')
        self.ui_btn_cancel.on_click(lambda btn: self._cancel_on_click(btn))

        self.ui_btn_default = \
            widgets.Button(description='Default',
                           tooltip='Load default settings')
        self.ui_btn_default.on_click(lambda btn: self._default_on_click(btn))

        self.ui_txt_error_msg = widgets.HTML(value='')

        # self.ui_btn_box = widgets.HBox([self.ui_btn_save, self.ui_btn_cancel])
        self.ui_btn_box = widgets.HBox([self.ui_btn_save])

        self.ui_footer = \
            widgets.Box(children=[self.ui_btn_default,
                                  self.ui_btn_box],
                        layout=widgets.Layout(display='flex',
                                              flex_flow='row',
                                              justify_content='space-between'))

        self.ui_widget = widgets.VBox([self.ui_tab,
                                       self.ui_txt_error_msg,
                                       self.ui_footer])

    def _clear_error(self):
        self.ui_txt_error_msg.value = ''

    def _show_error(self, error):
        self.ui_txt_error_msg.value = \
            f"<b><center><font color='red'>{error}</center></b>"

    def _show_info(self, info):
        self.ui_txt_error_msg.value = \
            f"<b><center><font color='blue'>{info}</center></b>"

    def _save_on_click(self, btn):
        self._clear_error()
        try:
            for page in self.pages:
                page.save()
            pass
        except Exception as e:
            self._show_error(e)

    def _cancel_on_click(self, btn):
        self._clear_error()
        # ToDo realize it!
        pass

    def _default_on_click(self, btn):
        self._clear_error()
        for page in self.pages:
            page.set_default()
        self._show_info(
            'Default settings loaded. Press save button to apply changes.')

    def widget(self):
        return self.ui_widget

    def show(self):
        display(self.widget())


def create_settings_view(settings_root=None):
    settings_sys = SystemSettings(settings_root)
    tabs = [ProxySettings(settings_sys)]
    view = SettingsView(tabs)
    return view
