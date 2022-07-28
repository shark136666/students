from unicodedata import name
import pyvisa
import json
import random
# visa.log_to_screen()


# Подключение к SNVNA
rm = pyvisa.ResourceManager('@py')
# Connect to a Socket on the local machine at 5025
# Use the IP address of a remote machine to connect to it instead
try:
    CMT = rm.open_resource('TCPIP0::localhost::5025::SOCKET')
except:
    print("Failure to connect to VNA!")
    print("Check network settings")
CMT.read_termination = '\n'
# Set a really long timeout period for slow sweeps
CMT.timeout = 1000



# функция декоратор
def command_wrapper(f):
    def wrapped(inst, command):
        # print('До функции')
        try:
            if key == "debug":
                print(command)
        except:
            pass
        response = f(inst, command)
        # print('После функции')
        error = inst.query('SYST:ERR?')
        if error != '0, No error':
            print(error)
        return response

    # print('декорируем', f)
    return wrapped


@command_wrapper
def query(inst, command):
    result = inst.query(command)
    return result


@command_wrapper
def write(inst, command):
    inst.write(command)


query(CMT, "*IDN?")
write(CMT,"SENS:BWID 300e9")

write(CMT, "TRIG:SOUR BUS")

Dictionar={}

path = r'C:\Users\student15\Desktop\lesson1\students\lesson5\lesson5.txt'
file= open(path, 'w')
Tune_value={10:Dictionar,30:Dictionar,50:Dictionar}
nametag=[]
nametag1=[]
PCH_value=[]
value={2:3,4:5,1:2,22:2}
value1={21:3,44:5512,1123:2333,222:2111}
# Dictionar["atthenuator"]["Tune_value"]["IF"]["PCH_value"]["trace"]["absolute"].update(value)
# Dictionar["atthenuator"]["Tune_value"]["IF"]["PCH_value"]["trace"]["diffrence"].update(value1)
result = {}
mass = [10,20,30]
iff = [300,3]
for i in mass:
    result[f'{i}'] = {'IF':{}}
    for j in iff:
        result[f'{i}']['IF'][f'{j}']={'Trace':{"absolute":{},"diffrence":{}}}
print(result)

