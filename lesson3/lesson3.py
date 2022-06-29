# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 09:28:15 2021

@author: kuzma.m
"""

import pyvisa as visa



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
#Пресет
CMT.write(f'SYST:PRES')

#Добавляем 16 трасс в канал 
CMT.write(f'CALC1:PAR:COUN 16')
#Выводим на консоль
trace_count = CMT.query(f'CALC1:PAR:COUN?')
print(f'кол-во трасс: {trace_count}')

#Привести трассы к виду 1 трасса s11, 2 трасса s22...16 трасса s1616
for i in range(1,17):
	CMT.write(f'CALC1:PAR{i}:DEF S{i}{i}')

#На каждую трассу добавить 2 маркера 1Ghz и 5.5 Ghz
for i in range(1,17):
	#Выбираем активную трассу
	CMT.write(f'CALC1:PAR{i}:SEL')
	
	#Включаем марки 1 и 2 
	CMT.write(f'CALC1:TRAC{i}:MARK1:STAT ON')
	CMT.write(f'CALC1:TRAC{i}:MARK2:STAT ON')

	#Выставляем 1Ghz и 5.5 Ghz
	CMT.write(f'CALC1:MARK1:X 1e9')
	CMT.write(f'CALC1:MARK2:X 55e8')
	
#Каждую четную трассу приветси к виду S номер трассы (номер трассы-1)
for i in range(1,17):
	
	#Изменяем четную трассу
	if i % 2 == 0:
		n = i-1
		CMT.write(f'CALC1:PAR{i}:DEF S{i}{n}')
	#Запрашиваем данные и выводим
	trace_def = CMT.query(f'CALC1:PAR{i}:DEF?')
	print("трасса №",i,"= ",trace_def)
	
	



