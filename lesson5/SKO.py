# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 09:28:15 2021
@author: kuzma.m
"""

import pyvisa as visa
import time
# Подключение к SNVNA
rm = visa.ResourceManager()
rm = visa.ResourceManager('@py')
try:
    CMT = rm.open_resource('TCPIP0::localhost::5025::SOCKET')
except:
    print("Failure to connect to VNA!")
    print("Check network settings")
#The VNA ends each line with this. Reads will time out without this
CMT.read_termination='\n'
#Set a really long timeout period for slow sweeps
CMT.timeout = 100000





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



#Пресет
write(CMT,f'SYST:PRES')
""" создание 12 трасс """

write(CMT,f'CALC:MST ON')
for i in range(1,4):
    CMT.write(f'CALC1:PAR:COUN {i}')
""" изменение 12 трасс на R T S """
count = 1
for i in range(1,2):

    
    write(CMT,f'CALC1:PAR{count}:DEF T{i}')
    write(CMT,f'CALC:PAR{count}:SPOR {i}')

    write(CMT,f'CALC1:PAR{count + 1}:DEF R{i}')
    write(CMT,f'CALC:PAR{count + 1}:SPOR {i}')

    write(CMT,f'CALC1:PAR{count + 2}:DEF S{i}{i}')

    count += 3 
""" Установить фильтр ПЧ 300 кГц """
write(CMT,f'SENS:BAND {3e3}')
time.sleep(1)

""" Частотный план """
write(CMT,f'SERV:SWE:FREQ:FACT')

""" аттенюатор: 10 """
write(CMT,f'SERV:RFCTL:POW:STAT 1')
write(CMT,f'SERV:RFCTL:POW:ATT 10')

""" установить Код ЦАП """
write(CMT,f'SERV:RFCTL:POW:DAC 6554')
"""
for i in range(1,4):
    write(CMT,f'CALC:PAR{i}:SEL')
    write(CMT,f'CALC:MATH:MEM')
    write(CMT,f'CALC:MATH:FUNC DIVide')
"""

