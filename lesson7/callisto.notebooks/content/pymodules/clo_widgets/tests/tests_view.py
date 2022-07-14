from ipywidgets import widgets
from IPython.display import display
import pandas as pd
import qgrid
import jp.qgridutils as qgridutils
import jp.widgetutils as widgetutils
import jp.locator as locator
import clo.utils.testutils as testutils
import os
from clo_widgets.discover_devices.discover_devices_view import (
    DeviceDiscoverWidget
)
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode


def create_manufacturer_registry():
    registry = {}
    PLANAR_NAME = 'Planar'
    CMT_NAME = 'CMT'
    registry['COPPER MOUNTAIN TECHNOLOGIES'] = CMT_NAME
    registry['CMT'] = CMT_NAME
    registry['PLANAR'] = PLANAR_NAME
    registry['PLANAR LLC'] = PLANAR_NAME
    return registry


_registry = create_manufacturer_registry()


def normalize_manufacturer_name(name):
    name = name.strip()
    return _registry.get(name.upper(), name)


class Model(object):
    def __init__(self):
        super().__init__()

        self._listeners = {}

        self.root_dir = None

        """
        manufacturers - dictionary {
            'manufacturer': dictionary {
                'model0': DeviceInformation class
                'model1': another DeviceInformation class
            }
        }
        """
        self.manufacturers = {}

    def on(self, names, handler):
        """
        Observe event {name} with {handler}.
        Handler - function with arguments event and model.
        """
        for n in names:
            self._listeners.setdefault(n, []).append(handler)

    def off(self, names, handler):
        """
        Stop observing event {name} with {handler}.
        Handler - function with arguments event and model.
        """
        for n in names:
            try:
                if handler is None:
                    del self._listeners[n]
                else:
                    self._listeners[n].remove(handler)
            except KeyError:
                pass

    def _notify_listeners(self, event):
        event_listeners = self._listeners.get(event['name'], [])
        for c in event_listeners:
            c(event, self)

    def set_root_dir(self, path):
        self.root_dir = path
        try:
            self.model = self._process_root_dir(path)
            self._notify_listeners({'name': 'new_root',
                                    'value': path})
        except Exception as e:
            self._notify_listeners({'name': 'error',
                                    'value': e})

    def clear(self):
        """
        Function clears model.
        """
        self.root_dir = None
        self.manufacturers = {}
        self._notify_listeners({'name': 'clear'})

    def _process_root_dir(self, path):
        dev_conf_paths = testutils.get_device_configs(path)

        devices = []
        for conf in dev_conf_paths:
            devices.extend(testutils.read_devices_info(conf))

        model = {}
        for d in devices:
            manufacturer = normalize_manufacturer_name(d.manufacturer)
            # getting container for manufacturer
            prod_cont = model.setdefault(manufacturer, {})
            prod_cont[d.name] = d

        return model

    def get_manufacturers(self):
        """
        Function returns set-like of device manufacturers
        """
        return self.model.keys()

    def get_models(self, manufacturer):
        """
        Function returns dictionary of device models for given manufacturer
        """
        return self.model.get(manufacturer, {}).keys()

    def get_operations(self, manufacturer, model):
        """
        Function returns list of allowed operations for device
        """
        dev_inf = self.model.get(manufacturer, {}).get(model)
        if dev_inf is None:
            return []

        return testutils.collect_device_tests(os.path.dirname(dev_inf.path))


def _create_execute_button(name):
    w = widgets.HTML(value='')
    w.name = name
    w.HTML_BUTTON_DISABLED = ('<button disabled style='
                              '"background-color: gray; color: white;"'
                              '>{name}</button>')
    w.HTML_BUTTON_WITH_LINK = \
        '''<button onclick="window.open('{link}', '_blank')">{name}</button>'''

    def set_link(link, name=None):
        if name is not None:
            w.name = name
        w.value = w.HTML_BUTTON_WITH_LINK.format(name=w.name,
                                                 link=link)

    def set_disabled(name=None):
        if name is not None:
            w.name = name
        w.value = w.HTML_BUTTON_DISABLED.format(name=w.name)

    w.set_link = set_link
    w.set_disabled = set_disabled

    w.set_disabled('select operation')

    return w


def _update_ops_table(table, operations):
    """
    :param table: qgrid
    :param operations: list of test information classes
    :return: nothing
    """
    fields = ['name', 'description']
    df = pd.DataFrame(
        [{fd: getattr(op, fd) for fd in fields} for op in operations],
        columns=fields)
    df.index += 1
    df.index.name = ''

    table.operations = operations

    # resetting selection before setting new data frame
    table.change_selection(rows=[])

    table.df = df

    if len(operations):
        table.change_selection(rows=[df.index[0]])


def _on_ops_selection_changed(table, callback):
    """
    :param table: qgrid
    :param callback: function(data)
    :return: nothing
    """
    data = {'selected': 0, 'url': '', 'exist': False}

    selected = table.get_selected_rows()
    if len(selected) != 1:
        callback(data)
        return

    selected = selected[0]

    op = table.operations[selected]
    file_path = op.start
    if not os.path.isabs(file_path):
        base_dir = os.path.dirname(op.path)
        file_path = os.path.join(base_dir, file_path)

    data['selected'] = 1
    data['exist'] = os.path.exists(file_path)
    if not data['exist']:
        file_path = os.path.join(os.path.dirname(os.path.abspath(
            __file__)), 'file_not_found.html')

    data['url'] = locator.file_url(file_path)
    callback(data)


def _create_select_from_list_widget(model):
    w = widgets.VBox(children=[])
    w.model = model
    w.ui_dd_manufacturer = widgets.Dropdown(
        description='Manufacturer:',
        style={'description_width': 'initial'})
    w.ui_dd_model = widgets.Dropdown(description='Model:')

    w.ui_ops_table = _create_operations_table()

    def _load_model_data():
        widgetutils.clear_dropdown(w.ui_dd_manufacturer)
        widgetutils.clear_dropdown(w.ui_dd_model)
        w.ui_dd_manufacturer.options = w.model.get_manufacturers()

    w.model.on(['new_root'], lambda event, model: _load_model_data())

    def _dd_manufacturer_on_change(change):
        if not widgetutils.dropdown_value_changed_event(change):
            return

        manufacturer = widgetutils.dropdown_new_value_from_event(change)
        models = w.model.get_models(manufacturer)
        w.ui_dd_model.options = models

    w.ui_dd_manufacturer.observe(_dd_manufacturer_on_change)

    def _dd_model_on_change(change):
        if not widgetutils.dropdown_value_changed_event(change):
            return

        w.ui_btn_execute.set_disabled('select operation')

        manufacturer = w.ui_dd_manufacturer.value
        model = widgetutils.dropdown_new_value_from_event(change)

        # operations is the list of TestInformation class
        operations = w.model.get_operations(manufacturer, model)

        _update_ops_table(w.ui_ops_table, operations)

    w.ui_dd_model.observe(_dd_model_on_change)

    def _ops_selection_cb(data):
        # data = {'selected': 0, 'url': '', 'exist': False}
        if data['selected'] == 1:
            url = data['url']

            if data['exist']:
                url_parts = list(urlparse(url))
                query = dict(parse_qsl(url_parts[4]))
                query.update({'manufacturer': w.ui_dd_manufacturer.value,
                              'model': w.ui_dd_model.value})

                url_parts[4] = urlencode(query)
                url = urlunparse(url_parts)

            w.ui_btn_execute.set_link(url, 'Execute')
        else:
            w.ui_btn_execute.set_disabled('select operation')

    def _ops_selection_changed(event, grid):
        _on_ops_selection_changed(grid, _ops_selection_cb)

    w.ui_ops_table.on('selection_changed', _ops_selection_changed)

    w.ui_btn_execute = _create_execute_button('Execute')

    w.ui_box_header = widgets.HBox([w.ui_dd_manufacturer, w.ui_dd_model])
    w.ui_box_bottom = widgets.Box(
        children=[w.ui_btn_execute],
        layout=widgets.Layout(display='flex',
                              flex_flow='row',
                              justify_content='flex-end'))

    w.children = [w.ui_box_header, w.ui_ops_table, w.ui_box_bottom]
    return w


def _create_chosen_device_widget(on_back=None):
    """
    on_back - function() without arguments
    """
    w = widgets.HBox(children=[])

    text_widgets_order = \
        ['manufacturer', 'model', 'serial', 'version', 'resource']

    def createTitleWidget(text):
        return widgets.Label(value=text[0].upper() + text[1:] + ':')

    w.text_widgets = \
        {text: widgets.Label(value='') for text in text_widgets_order}
    # [createTitleWidget(text)} for text in text_widgets_order]

    w.ui_box_titles = widgets.VBox(
        [createTitleWidget(text) for text in text_widgets_order])
    w.ui_box_values = \
        widgets.VBox([w.text_widgets[t] for t in text_widgets_order])
    w.ui_box_cont = widgets.Box(children=[w.ui_box_titles, w.ui_box_values])
    w.ui_box_cont.layout.margin = '0 auto'

    w.ui_back_btn = widgets.Button(description='<')
    w.ui_back_btn.layout.width = '30px'

    w.children = [w.ui_back_btn, w.ui_box_cont]

    if on_back is not None:
        w.ui_back_btn.on_click(lambda btn: on_back())

    def clear():
        for text_widget in w.text_widgets:
            text_widget.value = ''

    def set_device(device):
        """
        device - dictionary {
            'manufacturer': '',
            'model': '',
            'serial': '',
            'version': '',
            'resource': ''
        }
        """
        for key in device:
            text_widget = w.text_widgets.get(key, None)
            if text_widget is None:
                continue
            text_widget.value = device[key]

    def get_device():
        """
        Function returns device dictionary. See set_device funtion description.
        """
        device = {}
        for key in w.text_widgets:
            device[key] = w.text_widgets[key].value
        return device

    w.clear = clear
    w.set_device = set_device
    w.get_device = get_device

    return w


    w = widgets.HBox(children=[])


    def create_text_widgets(text):
        return widgets.HBox([widgets.Label(value=text),
                             widgets.Label(value='')])

    w.text_widgets = {
        'manufacturer': create_text_widgets('Manufacturer:'),
        'model': create_text_widgets('Model:'),
        'serial': create_text_widgets('Serial:'),
        'version': create_text_widgets('Version:'),
        'resource': create_text_widgets('Resource:'),
    }
    text_widgets_order = \
        ['manufacturer', 'model', 'serial', 'version', 'resource']
    w.ui_vbox_text = \
        widgets.VBox([w.text_widgets[n] for n in text_widgets_order])

    w.ui_back_btn = widgets.Button(description='<')
    w.ui_back_btn.style.width = '10px'

    if on_back is not None:
        w.ui_back_btn.on_click(lambda btn: on_back())

    w.children = [w.ui_back_btn, w.ui_vbox_text]

    def clear():
        for text_widget in w.text_widgets:
            text_widget.children[1].value = ''

    def set_device(device):
        """
        device - dictionary {
            'manufacturer': '',
            'model': '',
            'serial': '',
            'version': '',
            'resource': ''
        }
        """
        for key in device:
            text_widget = w.text_widgets.get(key, None)
            if text_widget is None:
                continue
            text_widget.children[1].value = device[key]

    def get_device():
        """
        Function returns device dictionary. See set_device funtion description.
        """
        device = {}
        for key in w.text_widgets:
            device[key] = w.text_widgets[key].children[1].value
        return device

    w.clear = clear
    w.set_device = set_device
    w.get_device = get_device

    return w


def _create_operations_table():
    cd = {'': {'toolTip': 'Number',
               'maxWidth': 50}}

    def suppress_cell_editing(row):
        return False

    w = qgrid.show_grid(pd.DataFrame(columns=['name', 'description']),
                        show_toolbar=False,
                        column_definitions=cd,
                        row_edit_callback=suppress_cell_editing)
    qgridutils.disable_multiselection(w)
    qgridutils.keep_selection_when_sorting(w)

    return w


def _create_select_from_lan_widget(model):
    w = widgets.Box(children=[])
    w.model = model

    w.ui_discover_view = DeviceDiscoverWidget()

    def on_back():
        w.children = [w.ui_discover_view.widget()]

    w.ui_chosen_dev = _create_chosen_device_widget(on_back)
    w.ui_ops_table = _create_operations_table()
    w.ui_btn_execute = _create_execute_button('Execute')
    w.ui_box_bottom = widgets.Box(
        children=[w.ui_btn_execute],
        layout=widgets.Layout(display='flex',
                              flex_flow='row',
                              justify_content='flex-end'))
    w.ui_chosen_box = widgets.VBox([w.ui_chosen_dev,
                                    w.ui_ops_table,
                                    w.ui_box_bottom])

    def _ops_selection_cb(data):
        # data = {'selected': 0, 'url': '', 'exist': False}
        if data['selected'] == 1:
            url = data['url']

            if data['exist']:
                url_parts = list(urlparse(url))
                query = dict(parse_qsl(url_parts[4]))
                query.update(w.ui_chosen_dev.get_device())

                url_parts[4] = urlencode(query)
                url = urlunparse(url_parts)

            w.ui_btn_execute.set_link(url, 'Execute')
        else:
            w.ui_btn_execute.set_disabled('select operation')

    def _ops_selection_changed(event, grid):
        _on_ops_selection_changed(grid, _ops_selection_cb)

    w.ui_ops_table.on('selection_changed', _ops_selection_changed)

    w.ui_box_bottom = widgets.Box(
        children=[w.ui_btn_execute],
        layout=widgets.Layout(display='flex',
                              flex_flow='row',
                              justify_content='flex-end'))

    def device_filter(device):
        return device['manufacturer'].upper() in _registry

    w.ui_discover_view.device_filter = device_filter

    def device_selected(device):
        w.ui_btn_execute.set_disabled('select operation')
        w.ui_chosen_dev.set_device(device)
        _update_ops_table(w.ui_ops_table,
                          w.model.get_operations(device['manufacturer'],
                                                 device['model']))
        w.children = [w.ui_chosen_box]

    w.ui_discover_view.device_selected = device_selected

    w.children = [w.ui_discover_view.widget()]

    return w


class TestsWidget(object):
    def __init__(self):
        super().__init__()

        self.model = Model()

        self.model.on(['error'],
                      lambda event, model: self._show_error(event['value']))

        self.ui_tglbtns = widgets.ToggleButtons(
            description='Select device:',
            options=['List', 'Discover'],
            value='List',
            disabled=False,
            button_style='',
            tooltips=['select device from list',
                      'select device from local network'],
            style={'description_width': 'initial'},
            layout=widgets.Layout(margin='auto auto 15px'))

        self.ui_tglbtns.observe(lambda change: self._on_tglbtn_change(change),
                                'value')

        self.ui_list_mode_widget = _create_select_from_list_widget(self.model)

        self.ui_txt_error_msg = widgets.HTML(value='')

        self.ui_active_widget = widgets.Box([])

        def create_list_config():
            w = _create_select_from_list_widget(self.model)

            def show():
                self.ui_active_widget.children = [w]

            def hide():
                pass

            return {'widget': w, 'show': show, 'hide': hide}

        def create_lan_config():
            w = _create_select_from_lan_widget(self.model)

            def show():
                self.ui_active_widget.children = [w]

            def hide():
                pass

            return {'widget': w, 'show': show, 'hide': hide}

        self.config = {
            'List': create_list_config(),
            'Discover': create_lan_config(),
        }

        self.ui_widget = widgets.VBox([self.ui_tglbtns,
                                       self.ui_txt_error_msg,
                                       self.ui_active_widget])

        self.config[self.ui_tglbtns.value]['show']()

    def _on_tglbtn_change(self, change):
        # {'name': 'value',
        #  'old': 'List',
        #  'new': 'Discover',
        #  'owner': ToggleButtons(...),
        #  'type': 'change'}
        self.config[change['old']]['hide']()
        self.config[change['new']]['show']()

    def _clear_error(self):
        self.ui_txt_error_msg.value = ''

    def _show_error(self, error):
        self.ui_txt_error_msg.value = \
            f"<b><center><font color='red'>{error}</center></b>"

    def set_root_dir(self, root_dir):
        self._clear_error()
        self.model.set_root_dir(root_dir)

    def widget(self):
        return self.ui_widget

    def show(self):
        display(self.widget())
