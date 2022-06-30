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

# функции
def convert (m, f):
    if  f == "GHz":
        m = m * 1000000000
    if  f == "kHz":
        m = m * 1000
    if  f == "MHz":
        m = m * 1000000
    return m

def ERR(connect):
    err = connect.query(f'SYST:ERR?')
    if  err != "0, No error":
       print(err)
   
def scan(connect):
    connect.write(f'TRIG:SOUR BUS')
    ERR(CMT)
    connect.write(f'INIT:CONT ON')
    ERR(CMT)
    connect.write(f'TRIG:SING')
    ERR(CMT)
    connect.query(f'*OPC?')
    ERR(CMT)
    

#Пресет
CMT.write(f'SYST:PRES')

# частота начала и конца росчерка
CMT.write(f'SENS:FREQ:STAR {convert(1, "GHz")}')
freq_star = CMT.query(f'SENS:FREQ:STAR?')
CMT.write(f'SENS:FREQ:STOP {convert(6, "GHz")}')
freq_stop = CMT.query(f'SENS:FREQ:STOP?')

# Установка кол-ва точек 
CMT.write(f'SENS:SWE:POIN 1001')
point = CMT.query(f'SENS:SWE:POIN?')

#Установка фильтра ПЧ
CMT.write(f'SENS:BAND {convert(3, "kHz")}')
band = CMT.query(f'SENS:BAND?')
time.sleep(1)

print ("Канал №1 start ", freq_star, "Gz | stop ", freq_stop, "Gz | point ", point, "| band ", band)

# создание маркеров
CMT.write(f'CALC:MARK1:STAT ON')
CMT.write(f'CALC:MARK2:STAT ON')
CMT.write(f'CALC:MARK3:STAT ON')
CMT.write(f'CALC:MARK4:STAT ON')

# раставление маркеров
CMT.write(f'CALC1:MARK1:X {convert(2, "GHz")}')
CMT.write(f'CALC1:MARK2:X {convert(3, "GHz")}')
CMT.write(f'CALC1:MARK3:X {convert(4, "GHz")}')
CMT.write(f'CALC1:MARK4:X {convert(5, "GHz")}')

# вкл статистику и номера рабочих маркеров 
CMT.write(f'CALC:MST ON')
CMT.write(f'CALC:MST:DOM ON')

Dict = {}

for i in range(1,5):
    if i == 4:
        CMT.write(f'CALC:MST:DOM:STAR {1}')
        ERR(CMT)
        CMT.write(f'CALC:MST:DOM:STOP {i}')
        ERR(CMT)
    else:
        CMT.write(f'CALC:MST:DOM:STAR {i}')
        ERR(CMT)
        CMT.write(f'CALC:MST:DOM:STOP {i+1}')
        ERR(CMT)
        
    a = CMT.query(f'CALC:MST:DATA?').split(',')
    b = CMT.query(f'CALC:MST:DOM:STAR?')
    c = CMT.query(f'CALC:MST:DOM:STOP?')
    Dict.update({f'{b} - {c}':{f'mean':f'{a[0]}', f's.dev':f'{a[1]}',f'p-p':f'{a[2]}'}})
for key, value in Dict.items():
	print(f'Маркеры {key}\n Среднее значение = {value["mean"]}\n Стандартное отклонение = {value["s.dev"]}\n Фактор пик-пик = {value["p-p"]}')

print('')
#Пресет
CMT.write(f'SYST:PRES')

#смена на S
CMT.write(f'CALC1:PAR1:DEf S21')

# вкл мат статистику
CMT.write(f'CALC:MST ON')

#однократный росчерк 
scan(CMT)

#Вывести значение mean
a = CMT.query(f'CALC:MST:DATA?').split(',')
print("mean = ",a[0])

#вкл усреднение
CMT.write(f'SENS:AVER ON')

#устанавливаем фактор усреднение
CMT.write(f'SENS:AVER:COUN 100')

print("Выполняем ",CMT.query(f'SENS:AVER:COUN?'),"росчерков ")
# выполнение 100 росчерков
for i in CMT.query(f'SENS:AVER:COUN?'):
    scan(CMT)

# вывод mean
a = CMT.query(f'CALC:MST:DATA?').split(',')
print("mean = ",a[0])



