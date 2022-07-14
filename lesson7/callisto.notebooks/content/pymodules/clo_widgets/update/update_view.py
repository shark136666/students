from ipywidgets import widgets
from IPython.display import display
from clo.git_update import GitUpdate
from clo.git_update_settings import GitUpdateSettings
from clo.environment import Environment
from clo.system_settings import SystemSettings
import jp.widgetutils as widgetutils

# ToDo update _upd before on click event handling


class NBUpdater(object):
    def __init__(self):
        super().__init__()

        self._upd = GitUpdate()

        self._upd.on('check_result',
                     lambda event, upd: self._check_updates_result(event, upd))
        self._upd.on('update_result',
                     lambda event, upd: self._update_result(event, upd))

        self.ui_btn_check_for_updates = \
            widgets.Button(description='Check for updates')
        self.ui_btn_check_for_updates.on_click(
            lambda btn: self._check_for_updates_on_click(btn))

        self.ui_txt_info = widgets.Label(value='')

        self.ui_btn_update = widgets.Button(description='Update')
        self.ui_btn_update.on_click(lambda btn: self._update_on_click(btn))

        self.ui_btn_block = \
            widgets.Box(children=[self.ui_btn_check_for_updates,
                                  self.ui_btn_update])

        self.ui_cont = \
            widgets.Box(children=[self.ui_txt_info,
                                  self.ui_btn_block],
                        layout=widgets.Layout(display='flex',
                                              flex_flow='row',
                                              justify_content='space-between'))

        self.ui_txt_error_msg = widgets.HTML(value='')

        self.ui_widget = widgets.VBox([self.ui_cont, self.ui_txt_error_msg])
        widgetutils.disable_widget(self.ui_btn_update)

    def check_for_updates(self):
        self._check_for_updates()

    def hide_check_updates_btn(self, hide=True):
        widgetutils.hide_widget(self.ui_btn_check_for_updates, hide)

    def _configure_update(self):
        sys_settings = SystemSettings()
        if not sys_settings.get_use_proxy():
            proxy = {}
        else:
            proxy = sys_settings.get_proxy()

        usettings = GitUpdateSettings()
        self._upd.repo_path = Environment.nb_dir()
        self._upd.repo_branch = usettings.branch()
        self._upd.remote_url = usettings.url()
        self._upd.git_path = usettings.git_path()
        self._upd.git_home = Environment.home_dir()
        self._upd.proxy = proxy

    def _lock_btns(self, lock=True):
        widgetutils.disable_widget(self.ui_btn_check_for_updates, lock)
        widgetutils.disable_widget(self.ui_btn_update, lock)

    def _show_information(self, info):
        self.ui_txt_info.value = info

    def _show_error(self, error):
        self.ui_txt_error_msg.value = \
            "<b><center><font color='red'>{error}</center></b>".format(
                error=error.replace('\n', '<br/>'))
        widgetutils.show_widget(self.ui_txt_error_msg)

    def _clear_error(self):
        self.ui_txt_error_msg.value = ''
        widgetutils.hide_widget(self.ui_txt_error_msg)

    def _check_for_updates_on_click(self, btn):
        self._check_for_updates()

    def _check_for_updates(self):
        self._clear_error()
        self._lock_btns()
        self._show_information('Checking for updates...')
        self._configure_update()
        self._upd.check_updates()

    def _update_on_click(self, btn):
        self._clear_error()
        self._lock_btns()
        self._show_information('Updating...')
        self._configure_update()
        self._upd.update()

    def _check_updates_result(self, event, upd):
        update_available = event['result']

        widgetutils.enable_widget(self.ui_btn_check_for_updates)
        widgetutils.enable_widget(self.ui_btn_update, update_available)

        error = event['error']
        if len(error) != 0:
            self._show_information('Error occured while checking updates')
            self._show_error(error)
            return

        if update_available:
            self._show_information('An update from {date} is available'.format(
                date=event['timestamp']))
        else:
            self._show_information('The latest version already installed')

    def _update_result(self, event, upd):
        update_result = event['result']

        widgetutils.enable_widget(self.ui_btn_check_for_updates)
        widgetutils.enable_widget(self.ui_btn_update, not update_result)

        error = event['error']
        if len(error) != 0:
            self._show_information('Error occured while updating')
            self._show_error(error)
            return

        if update_result:
            self._show_information('Latest version successfully installed')
        else:
            self._show_information('The latest version already installed')

    def widget(self):
        return self.ui_widget

    def show(self):
        display(self.widget())
