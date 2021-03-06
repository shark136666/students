# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 09:28:15 2021

@author: kuzma.m
"""

import visa 



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
CMT.write(f'CALC1:PAR:COUN 2')
trace_count = 2
CMT.write(f'CALC1:PAR:COUN {trace_count}')
#второй это получение данных из программы, он возвращает значения, их можно добавлять в переменные
trace_count = CMT.query(f'CALC1:PAR:COUN?')
print(trace_count)


