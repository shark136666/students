from ipywidgets import widgets
from IPython.display import display
import pandas as pd
import qgrid
import jp.qgridutils as qgridutils
import ipaddress
import clo.utils.visautils as visautils
import jp.widgetutils as widgetutils
import threading
from jp.apputils import run_in_main_thread


class DeviceDiscoverWidget(object):
    class _DiscoverThread(threading.Thread):
        def __init__(self, ip_range, port, progress_callback,
                     device_found_callback, finish_callback):
            super().__init__()
            self._stop_event = threading.Event()
            self.ip_range = ip_range
            self.port = port
            self.progress_callback = progress_callback
            self.device_found_callback = device_found_callback
            self.finish_callback = finish_callback

        def run(self):
            devices = []
            for addr in self.ip_range:
                if self.is_stop_requested():
                    break
                try:
                    self.progress_callback()
                    resource_name = 'TCPIP0::{addr}::{port}::SOCKET'.format(
                        addr=ipaddress.IPv4Address(addr).exploded,
                        port=self.port)
                    inf = visautils.identify_instrument(resource_name,
                                                        open_timeout=200)
                    inf = visautils.construct_identify_dict(inf)
                    inf['resource'] = resource_name
                    devices.append(inf)
                    self.device_found_callback(inf)
                except Exception:
                    pass
            self.finish_callback(devices, self.is_stop_requested())

        def stop(self):
            self._stop_event.set()

        def is_stop_requested(self):
            return self._stop_event.is_set()

    def __init__(self, device_filter=None, device_selected=None):
        if device_filter is not None:
            self.device_filter = self.device_filter
        else:
            self.device_filter = self._device_filter_default

        if device_selected is not None:
            self.device_selected = self._device_selected
        else:
            self.device_selected = self._device_selected_default

        self.ui_txt_address = \
            widgets.Text(value='192.168.1.0',
                         description='network address',
                         placeholder='192.168.1.0',
                         style={'description_width': 'initial'})
        self.ui_txt_subnet_mask = widgets.Label(value='/24')

        self.ui_btn_discover = \
            widgets.Button(description='Discover devices',
                           tooltip='Scan network for available devices')
        self.ui_btn_discover.root = self
        self.ui_btn_discover.on_click(self._btn_discover_on_click)

        self.ui_btn_discover_stop = \
            widgets.Button(description='Stop', tooltip='Stop discover process')
        self.ui_btn_discover_stop.root = self
        self.ui_btn_discover_stop.on_click(self._btn_discover_stop_on_click)

        self.ui_txt_error_msg = widgets.HTML(value='')

        self.ui_progress_bar = widgets.IntProgress(min=0, value=0)

        cd = {'': {'toolTip': 'Number',
                   'maxWidth': 50}}
        self.ui_devices_table = qgrid.show_grid(
            pd.DataFrame(columns=['manufacturer',
                                  'model',
                                  'serial',
                                  'version',
                                  'resource']),
            show_toolbar=False,
            column_definitions=cd)

        self.ui_devices_table.grid_options['editable'] = False

        qgridutils.disable_multiselection(self.ui_devices_table)
        qgridutils.keep_selection_when_sorting(self.ui_devices_table)

        self.ui_devices_table.on(
            'selection_changed',
            lambda event, table: self._dev_table_selection_changed_handler(
                event, table))

        self.ui_btn_choose_device = \
            widgets.Button(description='Choose device',
                           tooltip='Choose selected device')
        self.ui_btn_choose_device.root = self
        self.ui_btn_choose_device.on_click(self._btn_choose_device_on_click)

        self.ui_txt_address.layout.flex = '0 1 auto'
        self.ui_txt_subnet_mask.layout.flex = '1 1 auto'
        self.ui_btn_discover.layout.flex = '1 1 auto'
        self.ui_btn_discover_stop.layout.flex = '1 1 auto'
        self.ui_box_ctl = widgets.HBox([self.ui_txt_address,
                                        self.ui_txt_subnet_mask,
                                        self.ui_btn_discover,
                                        self.ui_btn_discover_stop])

        self.ui_box_bottom = \
            widgets.Box(children=[self.ui_progress_bar,
                                  self.ui_btn_choose_device],
                        layout=widgets.Layout(display='flex',
                                              flex_flow='row',
                                              justify_content='space-between'))

        # self.ui_btn_test = widgets.Button(description='Test')
        # self.ui_btn_test.root = self
        # self.ui_btn_test.on_click(self._btn_test_on_click)

        self.ui_widget = widgets.VBox([self.ui_box_ctl,
                                       self.ui_txt_error_msg,
                                       self.ui_devices_table,
                                       self.ui_box_bottom])
                                       # self.ui_btn_test])
        widgetutils.hide_widget(self.ui_progress_bar)
        widgetutils.disable_widget(self.ui_btn_discover_stop)
        widgetutils.disable_widget(self.ui_btn_choose_device)

    # @staticmethod
    # def _btn_test_on_click(btn):
    #     pass

    @staticmethod
    def _btn_discover_on_click(btn):
        self = btn.root

        self._clear_error()

        try:
            ipaddr = ipaddress.IPv4Address(self.ui_txt_address.value)
        except ipaddress.AddressValueError as e:
            self._show_error('Incorrect network address: {}'.format(str(e)))
            return

        if ipaddr.is_loopback:
            self._show_error('Discovering devices in loopback is impossible')
            return

        base = '.'.join(ipaddr.exploded.split('.')[:-1])
        ip = range(int(ipaddress.IPv4Address(base + '.1')),
                   int(ipaddress.IPv4Address(base + '.255')))

        self._discover_start(ip)

    @staticmethod
    def _btn_discover_stop_on_click(btn):
        self = btn.root

        widgetutils.disable_widget(btn)
        self._discover_thread.stop()
        self._discover_thread.join()

    def _dev_table_selection_changed_handler(self, event, table):
        selected = table.get_selected_rows()
        widgetutils.enable_widget(self.ui_btn_choose_device,
                                  len(selected) == 1)

    @staticmethod
    def _btn_choose_device_on_click(btn):
        self = btn.root
        grid = self.ui_devices_table
        df = grid.get_changed_df()
        selected = grid.get_selected_rows()[0]
        dev = {}
        for c in df.columns:
            dev[c] = df.at[df.index[selected], c]
        # invoke callback
        self.device_selected(dev)

    @staticmethod
    def _device_filter_default(device):
        """
        Function filtering devices found in local area network.
        Function returns boolean value. It returns True for matched device and
        false otherwise.

        device - dictionary with fields:
            'manufacturer', 'model', 'serial', 'version', 'resource'
        """
        return True

    @staticmethod
    def _device_selected_default(device):
        """
        Function for getting selected device by user.

        device - dictionary. See _device_filter_default description.
        """
        pass

    def _append_new_device(self, device):
        # getting datafram from the devices table widget
        df = self.ui_devices_table.get_changed_df()

        if df.index.size == 0:
            df = self.ui_devices_table.get_changed_df()
            # print('columns {}'.format(df.columns))
            df.loc[1] = [device.get(key, '') for key in df.columns]
            df.index.name = ''
            self.ui_devices_table.df = df
            return

        index = 1 if df.index.size == 0 else df.index.max() + 1
        obj = [(df.index.name, index)]
        for c in df.columns:
            obj.append((c, device.get(c, '')))

        self.ui_devices_table.add_row(row=obj)

    def _clear_device_table(self):
        self.ui_devices_table.df = self.ui_devices_table.df.iloc[0:0]
        # alternative df(df.index, inplace=True) (slower)
        widgetutils.disable_widget(self.ui_btn_choose_device)

    def _discover_start(self, ip, port=5025):
        self._set_discover_mode()
        self.ui_progress_bar.max = len(ip)

        @run_in_main_thread
        def progress_cb():
            self.ui_progress_bar.value += 1

        @run_in_main_thread
        def device_found_cb(device):
            if not self.device_filter(device):
                return
            self._append_new_device(device)

        @run_in_main_thread
        def finish_cb(devices, stop_flag):
            self._discover_result(devices)

        # debug
        # finish_cb(self.__dbg_get_discover_result(), False)
        # return

        self._discover_thread = \
            self._DiscoverThread(ip,
                                 port,
                                 progress_cb,
                                 device_found_cb,
                                 finish_cb)
        self._discover_thread.start()

    def _set_discover_mode(self, show=True):
        widgetutils.disable_widget(self.ui_btn_discover, show)
        widgetutils.enable_widget(self.ui_btn_discover_stop, show)
        if show:
            self._clear_device_table()
        widgetutils.show_widget(self.ui_progress_bar, show)
        self.ui_progress_bar.max = 0
        self.ui_progress_bar.value = 0

    def _discover_result(self, devices):
        self._set_discover_mode(False)

    def _clear_error(self):
        self.ui_txt_error_msg.value = ''

    def _show_error(self, error):
        self.ui_txt_error_msg.value = \
            f"<b><center><font color='red'>{error}</center></b>"

    def __dbg_get_discover_result(self):
        return [{'manufacturer': 'Planar',
                 'model': 'Obzor-804',
                 'serial': '',
                 'version': '19.1.3/1',
                 'resource': 'TCPIP0::3232235862::5025::SOCKET'},
                {'manufacturer': 'CMT',
                 'model': 'PLANAR-804/1',
                 'serial': '',
                 'version': '19.2.3/3',
                 'resource': 'TCPIP0::3232235940::5025::SOCKET'},
                {'manufacturer': 'COPPER MOUNTAIN TECHNOLOGIES',
                 'model': '',
                 'serial': '',
                 'version': '',
                 'resource': 'TCPIP0::3232235969::5025::SOCKET'},
                {'manufacturer': 'CMT',
                 'model': 'S5048',
                 'serial': '15047071',
                 'version': '19.2.3/2',
                 'resource': 'TCPIP0::3232235988::5025::SOCKET'}]

    @property
    def network_address(self):
        return self.ui_txt_address.value

    @network_address.setter
    def set_network_address(self, address):
        self.ui_txt_address.value = address

    def widget(self):
        return self.ui_widget

    def show(self):
        display(self.widget())
