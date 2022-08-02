from ctypes.wintypes import PPOINT
from inspect import trace
from itertools import count
from multiprocessing import Array
from re import T
from textwrap import indent
from typing import Counter
import pyvisa
import json
import configparser

rm = pyvisa.ResourceManager('@py')
try:
    CMT = rm.open_resource('TCPIP0::localhost::5025::SOCKET')
except:
    print("Failure to connect to VNA!")
    print("Check network settings")
CMT.read_termination = '\n'
CMT.timeout = 10000

def Convertor(n,freq):
	if freq == "kHz":
		return int(n*1e+3)
	elif freq == "MHz":
		return int(n*1e+6)
	elif freq == "GHz":
		return int(n*1e+9)
	else: return print("Incorrect value")

def AntiConvertor(number):
    number1=float(format(float(number),'.2f'))
    # number1=str(number1)
    if (number1) < 1000000:
        return str(float(number1)/1000) + ' kHz'
    if (number1) < 1000000000:
        return str(float(number1)/1000000) + ' MHz'
    return str(float(number1)/1000000000) + ' GHz'

def command_wrapper(f):
    def wrapped(inst, command):
        response = f(inst, command)
        error = inst.query('SYST:ERR?')
        if error != '0, No error':
            print(error)
            print(command)
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

def list_to_dict(arr, ports, param):    # Перевод arr в dict
    dict = {'max_value':0}
    params = []
    for i in range(len(arr)):
        params.append(arr[(i)])
        dict.update({f'{param}{i+1}{i+1}': params[i]})
    dict['max_value'] = max(params)
    return dict
# конвертация кГц, МГц, ГГц в Гц
config = configparser.ConfigParser()
config.read('config.cfg')
arr1=config['range']['ranges'].split(',')
arr2=[]
arr_start_mark1 = []
arr_end_mark1 = []
for i in range(len(arr1)):
    arr2.append(arr1[i].split(' '))


for i in range(len(arr2)):
    arr_start_mark1.append((Convertor(int(arr2[i][0]),arr2[i][1])))
    arr_end_mark1.append((Convertor(int(arr2[i][2]),arr2[i][3])))


# функция однократного россчерка
def one_scan(ch_num):
    CMT.write('TRIG:SOUR BUS')  # устанавливаем источник триггера на шину
    CMT.write(f"INIT{ch_num}:CONT OFF")  # включаем повторный режим запуска триггера
    # переходим в состояние ожидания триггера
    CMT.write('INIT')
    CMT.write('TRIG:SING')  # выполняем россчерк
    CMT.query('*OPC?')




write(CMT, 'SERVice:RFCTL:POWer:STATe 1')
write(CMT, 'SERVice:RFCTL:POWer:ATT 10')
write(CMT, f'SENS1:BWID {Convertor(10,"kHz")}')
write(CMT, 'SERV:RFCTL:POW:DAC 6554')
write(CMT, 'SERVice:SWEep:FREQuency:FACTory')
trace_count=int(query(CMT, f'SERV:PORT:COUNT?'))
b = query(CMT, 'SENS1:SEGM:DATA?').split(',')
arr_start_mark = []
arr_end_mark = []
pparray=[[0] * len(arr_end_mark) for i in range(trace_count*3)]
# print(len(arr_end_mark))
pparray1=[[0] * len(arr_end_mark1) for i in range(trace_count*3)]
for i in range(9, len(b), 6):
    b[i] = str(int(b[i]) * 2)   # домножение точек на 2
    arr_end_mark.append(b[i - 1])   # начальные координаты марки
    arr_start_mark.append(b[i - 2])     # конечные
upd_array = ','.join(b)
write(CMT, f'SENS1:SEGM:DATA {upd_array}')
d=0
pparray=[[0] * len(arr_end_mark) for i in range(trace_count*3)]
# print(len(arr_end_mark))
# print(b)
# print(arr_start_mark)
# print(arr_end_mark)
write(CMT, f'CALC1:PAR:COUN 1')
for i in range(trace_count*3):
    params = ['S', 'T', 'R']
    # T, R
    if i%3 != 0:
        write(CMT, f'CALC1:PAR1:DEF {params[i % 3]}{(i // 3) + 1}')
        # установка порта-источника
        write(CMT, f'CALC1:PAR1:SPOR {(i//3) + 1}')
    # S
    else:
        write(CMT, f'CALC1:PAR1:DEF {params[i%3]}{(i // 3) + 1}{(i // 3) + 1}')
    one_scan(1)
    for j in range(len(arr_end_mark1)):#CFG
        CMT.write(f'CALC1:MARK1:STAT ON')
        CMT.write(f'CALC1:MARK2:STAT ON')
        CMT.write(f'CALC1:MST ON')
        CMT.write(f'CALC1:MST:DOM ON')
        CMT.write(f'CALC1:MARK1:X {arr_start_mark1[j]}')
        CMT.write(f'CALC1:MARK2:X {arr_end_mark1[j]}')
        mst_data=CMT.query(f'CALC1:MST:DATA?')
        array = mst_data.split(',')
        pparray1[i][j]=format(float(array[2]), '.8f')
        CMT.write(f'CALC1:MARK1:STAT OFF')
        CMT.write(f'CALC1:MARK2:STAT OFF')
        CMT.write(f'CALC1:MST OFF')
        CMT.write(f'CALC1:MST:DOM OFF')
    for j in range(len(arr_end_mark)): # SEGMENT PLAN
        CMT.write(f'CALC1:MARK1:STAT ON')
        CMT.write(f'CALC1:MARK2:STAT ON')
        CMT.write(f'CALC1:MST ON')
        CMT.write(f'CALC1:MST:DOM ON')
        CMT.write(f'CALC1:MARK1:X {arr_start_mark[j]}')
        CMT.write(f'CALC1:MARK2:X {arr_end_mark[j]}')
        mst_data=CMT.query(f'CALC1:MST:DATA?')
        array = mst_data.split(',')
        pparray[i][j]=format(float(array[2]), '.8f')
        CMT.write(f'CALC1:MARK1:STAT OFF')
        CMT.write(f'CALC1:MARK2:STAT OFF')
        CMT.write(f'CALC1:MST OFF')
        CMT.write(f'CALC1:MST:DOM OFF')

S1=pparray1[0:-1:3]

T1=pparray1[1:-1:3]
R1=pparray1[2:-2:3]
R1.append(pparray1[(trace_count*3)-1])

S=pparray[0:-1:3]
T=pparray[1:-1:3]
R=pparray[2:-1:3]
print(max(max(S1)))
print(max(max(T1)))
print(max(max(R1)))
# print(max(max(S1)))
# print(max(max(T1)))
# print(max(max(R1)))

str_array=[]
str_array1=[]
print(pparray1)
print(S1)
print(T1)
print(R1)
Cfg_dict={"segment":{}}
Seg_dict={"segment":{}}

for i in range(len(arr_end_mark)):
    str_array.append(AntiConvertor(arr_start_mark[i])+' '+AntiConvertor(arr_end_mark[i]))
for i in range(len(arr_end_mark1)):
    str_array1.append(AntiConvertor(arr_start_mark1[i])+' '+AntiConvertor(arr_end_mark1[i]))
print(str_array)
print(str_array1)
# value = {"max_value":25, "S11":23, "S22":17, "S33":7, "S44":25}
# value1 = {"max_value":11,"R11":11, "R22":1, "R33":3, "R44":8, "T11":6, "T22":2, "T33":4, "T44":9}
# # result["segment"]["segment_range"]["trace"]["absolute"].update(value)
# # result["segment"]["segment_range"]["trace"]["otnosit"].update(value1)
counter=0
for i in str_array1:
    for j in range (0,trace_count):
        Cfg_dict["segment"][f'{i}'] = {'trace':{"absolute":{},"otnosit":{}}}
        #Cfg_dict["segment"][f'{i}']["trace"]["absolute"].update({"max_value": max(max(S1))})
        #Cfg_dict["segment"][f'{i}']["trace"]["otnosit"].update({"max_value": max(max(max(T1)),max(max(R1)))})
        Cfg_dict["segment"][f'{i}']["trace"]["absolute"][f'S{j+1}{j+1}']= S1[counter][j]
        Cfg_dict["segment"][f'{i}']["trace"]["otnosit"][f'T{j+1}{j+1}']= T1[counter][j]
        Cfg_dict["segment"][f'{i}']["trace"]["otnosit"][f'R{j+1}{j+1}']= R1[counter][j]
    if counter<trace_count:
        counter+=1
    else:
        counter=0
print(Cfg_dict)
# json_data=json.dumps(result, indent=4)
# print(json_data)
# json = open('freq_test.json', 'w')
# json.write(json_data)
# json.close()
# print(R)