from IPython.display import display, Markdown, Latex, Javascript
import emoji
import time
import ipywidgets as widgets
import ipython_blocking
def test_name(testname):
    
    #testname="Тест неравномерности АЧХ"

    display(Markdown('### 💠 {}'.format(testname)))
    #display(Markdown('> *' + time.ctime() +
    #                 '* <br>Connect Power Meter to `Port 1` and press *Run* 💡 ![](gif/714.gif)'))

    button = widgets.Button(
        description='Run',
        disabled=False,
        button_style='success',  # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',
        icon='play'
    )
    return(button)
def connect_wizard(button):
    
    button.layout.visibility = 'hidden'
    display(Markdown('### Инструкция: \
                        \n * Убедитесь, что запущено приложение в сервисном режиме \
                        \n * Включите сокет сервер \
                        \n * Убедитесь, что порт в поле "IP Address" совпадает с портом в программе \
                        \n * Нажмите кнопку "connect", пустые поля должны автоматически заполниться \
                        \n * После того, как все поля заполнились нажмите кнопку "continue"'))

    import visa
    import matplotlib
    import matplotlib.pyplot as plt
    import numpy as np

    class DeviceBundle(object):
        def __init__(self, name, rm, default_ip):    
            self.name = name
            self.rm = rm
            self.default_ip = default_ip
            self.inst = None
            auto_layout = widgets.Layout( width='auto', layout='align_self:center', )
            self.descr = widgets.Label(value=name, layout=auto_layout)
            self.ip = widgets.Text(
                value= default_ip,
                description = 'IP Address',
                disabled = False,
            )
            self.button = widgets.Button(
                description='Connect',
                disabled=False,
                button_style='',  # 'success', 'info', 'warning', 'danger' or ''
                tooltip='Click me',
                icon='gear',
                layout = auto_layout
            )     
            self.p = widgets.Text(
                value='',
                placeholder='<empty>',
                description='Producer:',
                disabled=True
            )
            self.m = widgets.Text(
                value='',
                placeholder='<empty>',
                description='Model:',
                disabled=True
            )
            self.s = widgets.Text(
                value='',
                placeholder='<empty>',
                description='Serial:',
                disabled=True
            )
            self.v = widgets.Text(
                value='',
                placeholder='<empty>',
                description='Version:',
                disabled=True
            )
            self.button.on_click(self.on_connect)
            self.__box = widgets.VBox([self.descr, self.ip, self.p, self.m, self.s, self.v, self.button])
        
        def on_connect(self, b):
            addr, port = self.ip.value.split(":", 2)
            open_timeout = 5000
            self.inst = self.rm.open_resource('TCPIP0::'+ addr + '::' + port + '::SOCKET',open_timeout=open_timeout)
            self.inst.write_termination = '\n'
            self.inst.read_termination = '\n'
            self.inst.timeout = 60000
            ans = self.inst.query("*IDN?")
            self.p.value, self.m.value, self.s.value, self.v.value = ans.split(', ', 3)
            
        def instance(self):
            return self.inst
        
        def box(self):
            return self.__box
        
    rm = visa.ResourceManager('@py')

    legacy = DeviceBundle('Legacy device', rm, '127.0.0.1:5024')
    ng = DeviceBundle('Nextgen device', rm, '127.0.0.1:5025')

    return(widgets.HBox([legacy.box()]),legacy,ng)

def wait_button():
    display(Markdown('### 💠 Подключите прибор и нажмите "Continue"'))
    button2 = widgets.Button(
        description='Continue',
        disabled=False,
        button_style='success',  # 'success', 'info', 'warning', 'danger' or ''
        tooltip='Click me',
        icon='gear'
    )
    return(button2)