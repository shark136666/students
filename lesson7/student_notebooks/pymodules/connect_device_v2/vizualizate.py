import ipywidgets as widgets
import pyvisa as visa
from IPython.display import display, Markdown, Latex, Javascript,clear_output


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
        self.button.on_click(self.on_connect)
        self.__box = widgets.VBox([self.ip, self.producer, self.model, self.serial, self.version, self.button])

    def on_connect(self, b):

        addr, port = self.ip.value.split(":", 2)
        try:
            clear_output(wait=True)
            display(self.__box)
            device = connect_to_device(addr, port)
            self.producer.value = device.producer
            self.model.value = device.model
            self.serial.value = device.serial_number
            self.version.value = device.version
            self.connection = device.connection
            print(f'Найден {self.model.value}')
        except:
            clear_output(wait=True)
            self.producer.value = ''
            self.model.value = ''
            self.serial.value = ''
            self.version.value = ''
            self.connection = ''
            display(self.__box)
            print('Прибор не найден')

    def box(self):
        return self.__box


def vizulizated_finds_devices():
    find_devices = find_device()
    if len(find_devices) == 0:
        print(f'устройвство не найдено')
    if len(find_devices) > 1:
        select_device = widgets.Dropdown(
            options=find_devices,
            description='Выберите устройвство:',
            style={'description_width': 'initial'},
            disabled=False,
        )
        return select_device
    else:
        select_device = widgets.Dropdown(
            options=find_devices,
            description='Выберите устройвство:',
            style={'description_width': 'initial'})
        return select_device


def advanced_search_device(_,s):
    instruction = Markdown('### Инструкция: \
                                \n * Убедитесь, что запущено приложение в сервисном режиме \
                                \n * Включите сокет сервер \
                                \n * Убедитесь, что порт в поле "IP Address" совпадает с портом в программе \
                                \n * Нажмите кнопку "connect", пустые поля должны автоматически заполниться \
                                \n * После того, как все поля заполнились нажмите кнопку "continue"')


    display(instruction)









