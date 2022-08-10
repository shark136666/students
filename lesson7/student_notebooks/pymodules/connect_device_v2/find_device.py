import configparser
import shutil
import webbrowser
from time import sleep
import copy
from ipywidgets import widgets

from tkinter import Tk, filedialog
import pyvisa as visa
from ipywidgets import Layout, Button, VBox, Label
from IPython.display import clear_output,display

from .connect import find_device, connect_to_device


class DeviceBundle:
    connection: visa.ResourceManager

    def __init__(self, ):

        self.ip = widgets.Text(
            value='127.0.0.1:5024',
            description='IP Address',
            disabled=False,
        )
        self.button = widgets.Button(
            description='Connect',
            disabled=False,
            button_style='',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Click me',
            icon='gear',

        )
        self.producer = widgets.Text(
            value='',
            placeholder='<empty>',
            description='Producer:',
            disabled=True
        )
        self.model = widgets.Text(
            value='',
            placeholder='<empty>',
            description='Model:',
            disabled=True
        )
        self.serial = widgets.Text(
            value='',
            placeholder='<empty>',
            description='Serial:',
            disabled=True
        )
        self.version = widgets.Text(
            value='',
            placeholder='<empty>',
            description='Version:',
            disabled=True
        )
        self.valid = widgets.Valid(
            value=False,
            description='Connection status',
            style={'description_width': 'initial'}
        )
        self.button.on_click(self.on_connect)

        self.__box = widgets.VBox(
            [self.ip, self.producer, self.model, self.serial, self.version, self.valid, self.button])

    def on_connect(self, b):

        addr, port = self.ip.value.split(":", 2)
        try:
            device = connect_to_device(addr, port)
            self.producer.value = device.producer
            self.model.value = device.model
            self.serial.value = device.serial_number
            self.version.value = device.version
            self.connection = device.connection
            self.valid.value = True
            self.button.style.button_color= 'lightgray'
            # print(f'Найден {self.model.value}')
        except:
            self.producer.value = ''
            self.model.value = ''
            self.serial.value = ''
            self.version.value = ''
            self.connection = ''
            self.valid.value = False
            # display(self.__box)
            # print('Прибор не найден')

    def box(self):
        return self.__box


class FindDevice(widgets.VBox):
    """A file widget that leverages tkinter.filedialog."""

    def __init__(self):
        super(FindDevice, self).__init__()
        # Add the selected_files trait
        # self.add_traits(files=traitlets.traitlets.List())
        # Create the button.
        find_devices = find_device()
        self.selected_device = None
        self.wizard = widgets.Dropdown(
            options=find_devices,
            description='Выберите гуся:',
            style={'description_width': 'initial'},
            layout={'width': 'max-content'},
            disabled=False,
        )
        self.model = None
        self.config_path = 'config\\'
        self.default_config = f'{self.config_path}default.txt'
        self.config = ''
        self.config_for_load_device = ''

        self.description = ''
        self.instruction = Label('### Инструкция: \
                                        \n * Убедитесь, что запущено приложение в сервисном режиме \
                                        \n * Включите сокет сервер \
                                        \n * Убедитесь, что порт в поле "IP Address" совпадает с портом в программе \
                                        \n * Нажмите кнопку "connect", пустые поля должны автоматически заполниться \
                                        \n * После того, как все поля заполнились нажмите кнопку "continue"')
        self.rescan = widgets.Button(
            description='Повторный поиск гуся',
            disabled=False,
            button_style='info',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Повторный поиск гуся на ферме',
        )

        def rescan_button_clicked(_):
            # print('click')
            self.wizard.options = find_device()

        self.rescan.on_click(rescan_button_clicked)

        self.advanced_search = widgets.Button(
            description='Расширенный поиск гуся',
            disabled=False,
            button_style='info',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Расширенный поиск гуся на ферме'
        )
        self.back_advanced_search_button = widgets.Button(
            description='Назад',
            disabled=False,
            button_style='info',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Назад'
        )

        def back_advanced_search_button_clicked(_):
            self.children = [self.wizard, self.rescan, self.advanced_search, self.select_device_continue_button]

        self.back_advanced_search_button.on_click(back_advanced_search_button_clicked)
        self.box = DeviceBundle().box()

        def advanced_search_button_clicked(_):
            # "linking function with output"
            self.children = [self.box, self.back_advanced_search_button, self.select_device_continue_button]

        self.advanced_search.on_click(advanced_search_button_clicked)

        self.select_device_continue_button = widgets.Button(
            description='Запускаем гуся',
            disabled=False,
            button_style='success',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Запускается гусь'
        )

        self.config_button = widgets.Button(
            description='Создать конфиг',
            disabled=False,
            button_style='info',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Создать конфиг',
            layout={'width': 'max-content'}

        )

        self.select_config_continue_button = widgets.Button(
            description='Продолжить',
            disabled=False,
            button_style='success',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='Продолжить'
        )

        def print_config(config):
            print('Выбранная конфигурация')
            for key in config:
                for i in config[key]:
                    print(f'{i}:{config[key][i]}')

        def select_device_continue_button_clicked(_):
            # "linking function with output"

            if self.selected_device is None:
                if 'Dropdown' in str(type(self.children[0])):
                    self.selected_device = self.wizard.value.connection
                    self.model = self.wizard.value.model.replace(' ','')
                    self.model = self.model.replace('/','-')
                elif self.children[0].children[2].value != '':
                    adr, port = self.children[0].children[0].value.split(':')
                    self.selected_device = connect_to_device(adr, port).connection
                    self.model = self.children[0].children[2].value.replace(' ','')
                else:
                    for i in range(2):
                        self.box.children[6].style.button_color = 'lightgray'
                        sleep(1)
                        self.box.children[6].style.button_color = 'red'
                        sleep(1)

            # ищем конфиг
            if self.model is not None:
                config = find_config()
                if config is None:
                    print(f'Конфигурация для {self.model} не найдена')
                    self.children = [self.config_button]
                else:
                    clear_output()
                    print_config(config)
                    #self.config = parse_config(config)
                    self.config = config
                    #self.config_for_load_device = parse_config(dict(config))
                    self.config_button.description = 'редактировать конфиг'
                    self.config_button.tooltip = 'редактировать конфиг'
                    box = VBox([self.config_button, self.rescan_config_button, self.select_config_continue_button])
                    #self.children = box
                    display(box)


        self.rescan_config_button = widgets.Button(
            description='обновить',
            disabled=False,
            button_style='info',  # 'success', 'info', 'warning', 'danger' or ''
            tooltip='обновить'
        )

        def rescan_config_on_click(b):
            clear_output()
            # display(edit_config_but)
            config = find_config()
            if config is not None:
                self.config = config
                #self.config_for_load_device = parse_config(config)
                print_config(self.config)
                self.config_button.description = 'редактировать конфиг'
                box = VBox([self.config_button, self.rescan_config_button, self.select_config_continue_button])
                # self.children = box
                display(box)

        self.rescan_config_button.on_click(rescan_config_on_click)

        def create_config_on_click(b):
            #default_config = 'config\default.txt'
            config = find_config()
            if config is not None:
                self.config = config
                #self.config_for_load_device = parse_config(config)
                webbrowser.open(self.config_path + self.model + '.txt')
            else:
                display(self.config_path)
                shutil.copyfile(self.default_config, str(self.config_path + self.model + '.txt'))
                self.config = find_config()
                #self.config_for_load_device = parse_config(find_config())
                #print(self.default_config)
                #print('model ',self.config_path + self.model)
                webbrowser.open(self.config_path + self.model + '.txt')
                self.children = [self.config_button,self.rescan_config_button]

        self.config_button.on_click(create_config_on_click)



        def find_config():
            config = configparser.ConfigParser()
            config.read(f'{self.config_path}{self.model}.txt', encoding='utf-8-sig')
            if len(config.sections()) == 0:
                return None
            else:
                return config

        self.select_device_continue_button.on_click(select_device_continue_button_clicked)
        self.select_config_continue_button.on_click(select_device_continue_button_clicked)
        self.children = [self.wizard, self.rescan, self.advanced_search, self.select_device_continue_button]


def parse_config(config: dict):
    factor_value = {
        'k': 10 ** 3,
        'm': 10 ** 6,
        'g': 10 ** 9
    }
    new_config = config.copy()
    for i in config['RANGE']:
        value = config['RANGE'][i]
        try:
            numeric, factor = value.split(' ')
            new_value = float(numeric) * factor_value[factor.lower()]
            # print(new_value)
            new_config['RANGE'][i] = str(new_value)
        except:
            pass
    return new_config


