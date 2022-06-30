# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 09:28:15 2021

@author: kuzma.m
"""

import time
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

#конвертации множителей kHz,MHz,GHz в герцы (число,множитель)


def CheckError():
	error_data = CMT.query(f'SYST:ERR?')
	if error_data != '0, No error':
		print(error_data)


def HzConvertor(n,k):
	if k == "kHz":
		return int(n*1e+3)
	elif k == "MHz":
		return int(n*1e+6)
	elif k == "GHz":
		return int(n*1e+9)
	else: return -1

#Пресет
CMT.write(f'SYST:PRES')

#Добавляем 1 трассу на канал
CMT.write(f'CALC1:PAR:COUN 1')

#Установить частототы росчерка 1Ghz и 6Ghz 
CMT.write(f'SENS:FREQ:STAR {HzConvertor(1,"GHz")}')
CheckError()
CMT.write(f'SENS:FREQ:STOP {HzConvertor(6,"GHz")}')
CheckError()

#Установливаем кол-во точек в канале 1001 (points) 
CMT.write(f'SENS:SWE:POIN 1001')
CheckError()

#Установливаем фильтр ПЧ(ширина полосы ПЧ) 3kHz 
#imposter
CMT.write(f'SENS:BWID {HzConvertor(3,"kHz")}')
time.sleep(1) 

#Считываем данные и выводим
star_data = CMT.query(f'SENS:FREQ:STAR?')
stop_data = CMT.query(f'SENS:FREQ:STOP?')
poin_data = CMT.query(f'SENS:SWE:POIN?')
band_data = CMT.query(f'SENS:BAND?')

print(f'Канал №1: Start = {star_data}; Stop = {stop_data}; Points = {poin_data}; IFBW = {band_data}')

#Добовляем 4 маркера
CMT.write(f'CALC1:TRAC1:MARK1:STAT ON')
CMT.write(f'CALC1:TRAC1:MARK2:STAT ON')
CMT.write(f'CALC1:TRAC1:MARK3:STAT ON')
CMT.write(f'CALC1:TRAC1:MARK4:STAT ON')

#Выставляем 2,3,4,5 Ghz соответсвенно
CMT.write(f'CALC1:MARK1:X {HzConvertor(2,"GHz")}')
CMT.write(f'CALC1:MARK2:X {HzConvertor(3,"GHz")}')
CMT.write(f'CALC1:MARK3:X {HzConvertor(4,"GHz")}')
CMT.write(f'CALC1:MARK4:X {HzConvertor(5,"GHz")}')

#Включаем статистику и получаем данные
CMT.write(f'CALC1:MST ON')
CMT.write(f'CALC1:MST:DOM ON')

#Создаем словарь
dictionary = {}

#Получам статистику между маркерами 1-2,2-3,3-4,4-1
for i in range(1,5):
	if i == 4:
		#статистика между маркерами 1-4
		CMT.write(f'CALC1:MST:DOM:STAR 1')
		CheckError()
		CMT.write(f'CALC1:MST:DOM:STOP 4')
		CheckError()
	else:
		#статистика между маркерами 1-2,2-3,3-4
		CMT.write(f'CALC1:MST:DOM:STAR {i}')
		CheckError()
		CMT.write(f'CALC1:MST:DOM:STOP {i+1}')
		CheckError()

	#запрашиваем данные и добовляем в словарь
	star_data = CMT.query(f'CALC1:MST:DOM:STAR?')
	#CheckError()
	stop_data = CMT.query(f'CALC1:MST:DOM:STOP?')
	#CheckError()
	mst_data = CMT.query(f'CALC:MST:DATA?')
	#CheckError()
	array = mst_data.split(',')
	dictionary.update({f'{star_data}-{stop_data}':{f'mean':f'{array[0]}',f's.dev':f'{array[1]}',f'p-p':f'{array[2]}'}})

#Выводим словарь
for key, value in dictionary.items():
	print(f'Маркеры {key}\n Среднее значение = {value["mean"]}\n Стандартное отклонение = {value["s.dev"]}\n Фактор пик-пик = {value["p-p"]}')


def singlescan(connect):
	connect.write(f'TRIG:SOUR BUS')
	CheckError()
	connect.write(f'INIT:CONT ON')
	CheckError()
	connect.write(f'TRIG:SING')
	CheckError()
	connect.write(f'*OPC?')
	
#Пресет
CMT.write(f'SYST:PRES')
CheckError()

#Установливаем трассу s21
CMT.write(f'CALC1:PAR1:DEF S21')

CheckError()

#Перевести тригер в режим BUS
CMT.write(f'TRIG:SOUR BUS')
CheckError()


#Включить математическую статистику для всего диапазона
CMT.write(f'CALC1:MST ON')

#Выполнить однократный росчерк 
singlescan(CMT)

#Выводим значение mean
a = CMT.query(f'CALC:MST:DATA?')
print(a)
CheckError()
array = a.split(',')
CheckError()
print(f'mean = {array[0]}')

#Включили усреднение
CMT.write(f'SENS:AVER')
time.sleep(1) 
CheckError()

#Установили фактор усреднения 100
CMT.write(f'SENS1:AVER:COUN 100')
time.sleep(1) 
CheckError()

#Выполняем рочерк 100 раз
aver_data = CMT.query(f'SENS1:AVER:COUN?')


print(f'aver_data = {aver_data}')

for i in range(int(100)):
	singlescan(CMT)
	
#Выводим значение mean
mst_data = CMT.query(f'CALC:MST:DATA?')
array = mst_data.split(',')
print(f'mean = {array}')
