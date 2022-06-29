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
##############################################
# Есть два типа запросов 
# первый это отправить данные в программу
CMT.write(f'')
# примеры использования
trace_count = 1
n = 17
CMT.write(f'')
while trace_count < n:    
    CMT.write(f'CALC1:PAR:COUN {trace_count}')                              #создает трассу
    CMT.write(f'CALC1:PAR{trace_count}:DEF S{trace_count}{trace_count}')    # меняет S
    CMT.write(f'CALC1:TRAC{trace_count}:MARK1:STAT ON;:CALC1:TRAC{trace_count}:MARK2:STAT ON;:CALC1:TRAC{trace_count}:MARK1:X 3e9')#;:CALC1:TRAC1:MARK2:X 35e8
    trace_count += 1

f = input()
trace_count = 1
while trace_count < n: # изменение  S{trace_count}{trace_count-1} у четных
    if trace_count % 2 == 0:
        CMT.write(f'CALC1:PAR{trace_count}:DEF S{trace_count}{trace_count-1}')  # меняет S
        trace_def = CMT.query(f'CALC1:PAR{trace_count}:DEF?')
        print("трасса №",trace_count," = S",trace_def)
    else:
        trace_def = CMT.query(f'CALC1:PAR{trace_count}:DEF?')
        print("трасса №",trace_count," = S",trace_def)
    trace_count += 1


#второй это получение данных из программы, он возвращает значения, их можно добавлять в переменные
trace_count = CMT.query(f'CALC1:PAR:COUN?')
print("Трасс ",trace_count)


