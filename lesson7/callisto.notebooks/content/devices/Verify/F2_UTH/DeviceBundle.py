import ipywidgets as widgets
import visa
import time

class DeviceBundle(object):
    callbacks = None

    def onConnected(self, callback):
        if self.callbacks is None:
            self.callbacks = []        
        self.callbacks.append(callback)

    def trigger(self):
        if self.callbacks is not None:
            for callback in self.callbacks:
                callback(self)
                
    def __init__(self, name, rm, default_ip): 
        self._connected = False
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
            icon='wifi',
            layout = auto_layout
        )     
        self.p = widgets.Text(
            value='',
            placeholder='<empty>',
            description='Producer:',
            disabled=True
        )
        self.p.layout.visibility = 'hidden'
        self.m = widgets.Text(
            value='',
            placeholder='<empty>',
            description='Model:',
            disabled=True      
        )
        self.m.layout.visibility = 'hidden'
        self.s = widgets.Text(
            value='',
            placeholder='<empty>',
            description='Serial:',
            disabled=True          
        )
        self.s.layout.visibility = 'hidden'
        self.v = widgets.Text(
            value='',
            placeholder='<empty>',
            description='Version:',
            disabled=True
        )
        self.v.layout.visibility = 'hidden'
        self.button.on_click(self.on_connect)
        self.__box = widgets.VBox([self.descr, self.button, self.ip, self.p, self.m, self.s, self.v])
    
    def on_connect(self, b):
        self.button.disabled = True
        self.button.icon='hourglass-half'
        self.button.description = 'Connecting...'
        addr, port = self.ip.value.split(":", 2)
        try:
            self.inst = self.rm.open_resource('TCPIP0::'+ addr + '::' + port + '::SOCKET')
        except visa.VisaIOError as e:
            print(e)
            self.button.icon='exclamation-triangle'
            self.button.disabled = False
            self.button.description = 'Connection failed'
            self.button.button_style='danger'
            time.sleep(0.5)
            self.button.description = 'Connect'
            self.button.button_style=''
            self.button.icon='wifi'
            return
        self.inst.write_termination = '\n'
        self.inst.read_termination = '\n'
        #self.inst.chunk_size = 102400
        self.inst.timeout = 5000
        ans = self.inst.query("*IDN?")
        self.p.value, self.m.value, self.s.value, self.v.value = ans.split(', ', 3)
        self.button.button_style='success'
        self.button.icon='check'
        self.button.description = 'Connected'        
        self.p.layout.visibility = 'visible'
        self.m.layout.visibility = 'visible'
        self.s.layout.visibility = 'visible'
        self.v.layout.visibility = 'visible'
        self._connected = True
        self.trigger()
        
    def instance(self):
        return self.inst
    
    def box(self):
        return self.__box
    def is_connected(self):
        return self._connected