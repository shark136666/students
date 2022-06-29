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

#добавить трассу в канал
CMT.write(f'CALC1:PAR:COUN 2')
time.sleep(1)

#изменение измеряемого параметра S11 на графике 2 на S22
CMT.write(f'CALC:PAR2:DEF S22')
time.sleep(1)

#добавить маркер на трассу
CMT.write(f'CALC:MARK1:ACT')

CMT.write(f'CALC:MARK2:ACT')
time.sleep(1)

#изменить частоту маркера по оси Стимула Икс
CMT.write(f'CALC:MARK1:X 3000000000') #3 герц

CMT.write(f'CALC:MARK2:X 3500000000') #3,5 герц
time.sleep(1)

#удаление маркеров если они есть
marker_check = CMT.query('CALC:MARK?')
if marker_check: CMT.write(f'CALC:MARK OFF')
time.sleep(1)

#удаление графика
CMT.write(f'CALC1:PAR:COUN 1')

#это были некоторые команды из lesson2

#добавим 16 трасс в канал
CMT.write(f'CALC:PAR:COUN 16')
trace_count = CMT.query('CALC:PAR:COUN?')
print('всего графиков: ', trace_count)

#Привести трассы к виду 1 трасса s11, 2 трасса s22...16 трасса s1616
#count = 1
#while count <= trace_count:
   # CMT.write(f'CALC:PAR2:DEF S{c}')
   # count += 1
#На каждую трассу добавить 2 маркера 1 GHz и 5.5 GHz

#Каждую четную трассу привести к виду S номер трассы (номер трассы-1)

#Вывести в консоль все трассы
#пример 
#трасса №1 = s11
