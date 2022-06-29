# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 09:28:15 2021
@author: kuzma.m
"""

import pyvisa as visa


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
trace_count = 1
"""
print ("Введите колличество трасс")
n = int(input(int)) + 1
"""
n = 17
while trace_count < n:    
    CMT.write(f'CALC1:PAR:COUN {trace_count}')                              # создает трассу
    
    CMT.write(f'CALC1:PAR{trace_count}:DEF S{trace_count}{trace_count}')    # меняет S

    CMT.write(f'CALC:PAR{trace_count}:SEL')                                 # выбор трассы
    
    CMT.write(f'CALC1:TRAC{trace_count}:MARK1:STAT ON;:')                   # создание 1 маркера
    CMT.write(f'CALC1:TRAC{trace_count}:MARK2:STAT ON')                     # создание 2 маркера
    CMT.write(f'CALC1:MARK1:X 1e9')                                         # смещение на  1 GHz
    CMT.write(f'CALC1:MARK2:X 55e8')                                        # смещение на  5.5 GHz
    
    trace_count += 1

f = input()                                                                 # прост для ожидания
trace_count = 1

while trace_count < n:                                                      # изменение  S{trace_count}{trace_count-1} у четных
    if trace_count % 2 == 0:
        CMT.write(f'CALC1:PAR{trace_count}:DEF S{trace_count}{trace_count-1}')  # меняет S
        trace_def = CMT.query(f'CALC1:PAR{trace_count}:DEF?')
        print("трасса №",trace_count," = S",trace_def)
    else:
        trace_def = CMT.query(f'CALC1:PAR{trace_count}:DEF?')
        print("трасса №",trace_count," = S",trace_def)
    trace_count += 1

trace_count = CMT.query(f'CALC1:PAR:COUN?')

print("Всего трасс ",trace_count)                                       


