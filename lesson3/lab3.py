# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 09:28:15 2021

@author: kuzma.m
"""

import pyvisa as visa


# Подключение к SNVNA
rm = visa.ResourceManager('@py')
#Connect to a Socket on the local machine at 5025
#Use the IP address of a remote machine to connect to it instead
try:
    CMT = rm.open_resource('TCPIP0::localhost::5025::SOCKET')
except:
    print("Failure to connect to VNA!")
    print("Check network settings")

#The VNA ends each line with this. Reads will time out without this
CMT.read_termination='\n'
#Set a really long timeout period for slow sweeps
CMT.timeout = 100000



# Добавление 16 трасс
def traces_add(traces_count):
    CMT.write(f'CALC1:PAR:COUN {traces_count}')

traces_add(16)


# приведение трасс к виду 1 трасса s11, 2 трасса s22
def params_change():
    trace_count = CMT.query(f'CALC1:PAR:COUN?')
    for i in range(1, int(trace_count)+1):
        # без задержки запрос не успевает обрабатываться
        # используем *OPC? для получения информации об окончании процесса
        CMT.write(f'CALC1:PAR{i}:DEF S{str(i) * 2}; *OPC?')
        CMT.read()

params_change()


# добавление 2-ух маркеров на каждую трассу на 1GHz и 5.5 GHz
def markers_add():
    trace_count = CMT.query(f'CALC1:PAR:COUN?')
    CMT.write(f'CALC1:MARK{int(trace_count)*2}:ACT')
    for i in range(1, int(trace_count) + 1):
        CMT.write(f'CALC1:MARK{int(i)*2}:X 5.5e9;*OPC?')
        CMT.read()
        CMT.write(f'CALC1:MARK{(int(i) * 2)-1}:X 1e9;*OPC?')
        CMT.read()

markers_add()


# приведение четных трасс к виду S номер трассы (номер трассы-1)
def params_change_even():
    trace_count = CMT.query(f'CALC1:PAR:COUN?')
    for i in range(2, int(trace_count)+1, 2):
        trace_param = CMT.query(f'CALC1:PAR{i}:DEF?')
        trace_param = int(trace_param.replace('S', ''))
        CMT.write(f'CALC1:PAR{i}:DEF S{trace_param-1}; *OPC?')
        CMT.read()

params_change_even()

# Вывод всех трасс на консоль
def traces_output():
    trace_count = CMT.query(f'CALC1:PAR:COUN?')
    print(f'Trace count {trace_count}')
    for i in range(1, int(trace_count)+1):
        print(f'трасса {i} = ' + CMT.query(f'CALC1:PAR{i}:DEF?'))

traces_output()
