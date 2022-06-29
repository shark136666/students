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

#Пресет
CMT.write(f'SYST:PRES')

n = 17
while trace_count < n:
    # создает трассу
    CMT.write(f'CALC1:PAR:COUN {trace_count}')
    
    # меняет S
    CMT.write(f'CALC1:PAR{trace_count}:DEF S{trace_count}{trace_count}')
    
    # выбор трассы
    CMT.write(f'CALC:PAR{trace_count}:SEL')
    
    # создание 1 и 2 маркера 
    CMT.write(f'CALC1:TRAC{trace_count}:MARK1:STAT ON;:')
    CMT.write(f'CALC1:TRAC{trace_count}:MARK2:STAT ON')
    
    #Выставляем 1Ghz и 5.5 Ghz 
    CMT.write(f'CALC1:MARK1:X 1e9')
    CMT.write(f'CALC1:MARK2:X 55e8')

    # прибовляем в счетчик
    trace_count += 1

trace_count = 1

# изменение  S{trace_count}{trace_count-1} у четных и выводим трассу
while trace_count < n:                                                    
    if trace_count % 2 == 0:
        CMT.write(f'CALC1:PAR{trace_count}:DEF S{trace_count}{trace_count-1}')
    trace_def = CMT.query(f'CALC1:PAR{trace_count}:DEF?')

    print("трасса №",trace_count," = S",trace_def)
    trace_count += 1
    
# вывод трассы
trace_count = CMT.query(f'CALC1:PAR:COUN?')
print("Всего трасс ",trace_count)                                       


