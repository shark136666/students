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

def setup_trace(CMT, port, traces,ranges):
    write(CMT, f'CALC1:PAR:COUN 3')
    for trace in traces:
        if trace is "S":
            write(CMT, f'CALC1:PAR1:DEF {trace}{port}{port}')
            setup_markers(CMT,1,ranges)
        elif trace is "T":
            write(CMT, f'CALC1:PAR2:DEF {trace}{port}')
            write(CMT, f'CALC1:PAR2:SPOR {port}')
            setup_markers(CMT,2,ranges)
        else:
            write(CMT, f'CALC1:PAR3:DEF {trace}{port}')
            write(CMT, f'CALC1:PAR3:SPOR {port}')
            setup_markers(CMT,3,ranges)

def Convertor(n,freq):
	if freq == "kHz":
		return int(n*1e+3)
	elif freq == "MHz":
		return int(n*1e+6)
	elif freq == "GHz":
		return int(n*1e+9)
	else: return print("Incorrect value")

def Convertor1(value:str):    
    n,freq = value.split(' ')
    n=int(n)
    print(n,freq)
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
# конвертация кГц, МГц, ГГц в Гц

def get_ranges(ranges):
    result = {}
    arr=ranges.split(',')
    for i in range(len(arr)):
        result[i]={}        
        arr1 = arr[i].split('-')    
        result[i]['start'] = Convertor1(arr1[0])
        result[i]['stop'] = Convertor1(arr1[1])
    print(f'resul = {result}')
    return result

# функция однократного россчерка
def one_scan(CMT):
    CMT.write('TRIG:SOUR BUS')  # устанавливаем источник триггера на шину
    CMT.write(f"INIT:CONT OFF")  # включаем повторный режим запуска триггера
    # переходим в состояние ожидания триггера
    CMT.write('INIT')
    CMT.write('TRIG:SING')  # выполняем россчерк
    CMT.query('*OPC?')

def multiplier_segments(CMT):
    b = query(CMT, 'SENS1:SEGM:DATA?').split(',')       
    # print(len(arr_end_mark))    
    for i in range(9, len(b), 6):
        b[i] = str(int(b[i]) * 2)   # домножение точек на 2
             # конечные
    upd_array = ','.join(b)
    write(CMT, f'SENS1:SEGM:DATA {upd_array}')


def setup_chanel_parametrs(CMT,att, ifbw):
    write(CMT,'SYST:PRES')
    write(CMT, 'SERVice:RFCTL:POWer:STATe 1')
    write(CMT, f'SERVice:RFCTL:POWer:ATT {att}')
    write(CMT, f'SENS1:BWID {ifbw}')
    write(CMT, 'SERV:RFCTL:POW:DAC 6554')
    write(CMT, 'SERVice:SWEep:FREQuency:FACTory')
    multiplier_segments(CMT)
            
def setup_markers(CMT,trace,ranges):
        CMT.write(f'CALC1:PAR{trace}:SEL')
        marker_count=len(ranges)*2
        CMT.write(f'CALC1:MARK{marker_count}:STAT ON')
        CMT.write(f'CALC1:MST ON')
        CMT.write(f'CALC1:MST:DOM ON')
        for key in ranges.keys():
            # ((key+1) * 2 ) - 1 start
            # # ((key+1) * 2 ) stop
            CMT.write(f'CALC1:MARK{((key+1) * 2 ) - 1}:X {ranges[key]["start"]}')
            CMT.write(f'CALC1:MARK{((key+1) * 2 )}:X {ranges[key]["stop"]}')
        mst_data=CMT.query(f'CALC1:MST:DATA?')
        array = mst_data.split(',')

def get_data(CMT,port,key,result):
    for i in range(1,4):
        CMT.write(f'CALC1:PAR{i}:SEL')
        # ((key+1) * 2 ) - 1 start
        # # ((key+1) * 2 ) stop
        CMT.write(f'CALC1:MARK{((key+1) * 2 ) - 1}:FUNC:DOM:STAR')
        CMT.write(f'CALC1:MARK{((key+1) * 2 )}:FUNC:DOM:STOP')
        mst_data=CMT.query(f'CALC1:MST:DATA?')
        value = mst_data.split(',')[2]
        value = format(float(value,'.8f'))
        if i == 1:
            valueS=format(float(value,'.8f'))
            result['segment'][f'{start}-{stop}']['absolute'][f'S{port}{port}']={valueS}
            elif i == 2:
                valueT=format(float(value,'.8f'))
                result['segment'][f'{start}-{stop}']['otnosit'][f'T{port}{port}']={valueT}
                else:
                    valyeR=format(float(value,'.8f'))
                    result['segment'][f'{start}-{stop}']['otnosit'][f'R{port}{port}']={valueR}
    return result






config = configparser.ConfigParser()
config.read('config.cfg')
ranges = get_ranges(config['range']['ranges'])
IFBW = Convertor1(config['options']['IFBW'])
attenuator = config['options']['attenuator']
traces = ['S','T','R']
params=[1,2,3]
setup_chanel_parametrs(CMT,attenuator,IFBW)
trace_count=int(query(CMT, f'SERV:PORT:COUNT?'))


result={"segment":{}}
for port in range(1,trace_count+1):   
    setup_trace(CMT,port,traces,ranges)
    one_scan(CMT)
    for key in ranges.keys():
        print(key)
        start = ranges[key]['start']
        stop = ranges[key]['stop']
        result['segment'][f'{start}-{stop}']={"absolute": {},"otnosit":{}}
        get_data(CMT,port,key,result) # передаём ключ т.к он отображает позицию маркера (не сможет позиция верно сработать то будем фигачить диапазоном)







# arr2=[]
# arr_start_mark1 = []
# arr_end_mark1 = []
# for i in range(len(arr1)):
#     arr2.append(arr1[i].split(' '))



            




# for i in range(len(arr2)):
#     arr_start_mark1.append((Convertor(int(arr2[i][0]),arr2[i][1])))
#     arr_end_mark1.append((Convertor(int(arr2[i][2]),arr2[i][3])))





# trace_count=int(query(CMT, f'SERV:PORT:COUNT?'))



# d=0
# pparray=[[0] * len(arr_end_mark) for i in range(trace_count*3)]
# # print(len(arr_end_mark))
# # print(b)
# # print(arr_start_mark)
# # print(arr_end_mark)
# write(CMT, f'CALC1:PAR:COUN 1')
# for i in range(trace_count*3):
#     params = ['S', 'T', 'R']
#     # T, R
#     if i%3 != 0:
#         write(CMT, f'CALC1:PAR1:DEF {params[i % 3]}{(i // 3) + 1}')
#         # установка порта-источника
#         write(CMT, f'CALC1:PAR1:SPOR {(i//3) + 1}')
#     # S
#     else:
#         write(CMT, f'CALC1:PAR1:DEF {params[i%3]}{(i // 3) + 1}{(i // 3) + 1}')
#     one_scan(1)
#     for j in range(len(arr_end_mark1)):#CFG
#         CMT.write(f'CALC1:MARK1:STAT ON')
#         CMT.write(f'CALC1:MARK2:STAT ON')
#         CMT.write(f'CALC1:MST ON')
#         CMT.write(f'CALC1:MST:DOM ON')
#         CMT.write(f'CALC1:MARK1:X {arr_start_mark1[j]}')
#         CMT.write(f'CALC1:MARK2:X {arr_end_mark1[j]}')
#         mst_data=CMT.query(f'CALC1:MST:DATA?')
#         array = mst_data.split(',')
#         pparray1[i][j]=format(float(array[2]), '.8f')
#         CMT.write(f'CALC1:MARK1:STAT OFF')
#         CMT.write(f'CALC1:MARK2:STAT OFF')
#         CMT.write(f'CALC1:MST OFF')
#         CMT.write(f'CALC1:MST:DOM OFF')


# S1=pparray1[0:-1:3]

# T1=pparray1[1:-1:3]
# R1=pparray1[2:-2:3]
# R1.append(pparray1[(trace_count*3)-1])

# S=pparray[0:-1:3]
# T=pparray[1:-1:3]
# R=pparray[2:-1:3]
# print(max(max(S1)))
# print(max(max(T1)))
# print(max(max(R1)))
# # print(max(max(S1)))
# # print(max(max(T1)))
# # print(max(max(R1)))

# str_array=[]
# str_array1=[]
# print(pparray1)
# print(S1)
# print(T1)
# print(R1)
# Cfg_dict={"segment":{}}


# for i in range(len(arr_end_mark1)):
#     str_array1.append(AntiConvertor(arr_start_mark1[i])+' '+AntiConvertor(arr_end_mark1[i]))
# counter=0
# j=0
# for i in str_array1:
#     Cfg_dict["segment"][f'{i}'] = {'trace':{"absolute":{},"otnosit":{}}}
#     Cfg_dict["segment"][f'{i}']["trace"]["absolute"]={f"S{j+1}{j+1}" : f"{S1[j][counter]}" for j in range (0,trace_count)}
#     trace = f"T{j+1}{j+1}"
#     print(trace)
#     Cfg_dict["segment"][f'{i}']["trace"]["otnosit"][trace] = 1
#     # Cfg_dict["segment"][f'{i}']["trace"]["otnosit"]={f"R{j+1}{j+1}" : f"{R1[j][counter]}" for j in range (0,trace_count)}
#     if counter<trace_count:
#         counter+=1
#     else:
#         counter=0
# print(Cfg_dict)
# json_data=json.dumps(Cfg_dict, indent=4)
# print(json_data)
# json = open('freq_test.json', 'w')
# json.write(json_data)
# json.close()
# print(R)
