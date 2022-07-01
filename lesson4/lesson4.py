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
# Connect to a Socket on the local machine at 5025
# Use the IP address of a remote machine to connect to it instead
try:
    CMT = rm.open_resource('TCPIP0::localhost::5025::SOCKET')
except:
    print("Failure to connect to VNA!")
    print("Check network settings")

# The VNA ends each line with this. Reads will time out without this
CMT.read_termination = '\n'
# Set a really long timeout period for slow sweeps
CMT.timeout = 100000

##############################################

def hz_converter(value, selected_value):
    if selected_value == 1:
        Hz = value * 1000
        return Hz
        #print(value, ' Килогерц = ', Hz, ' Герц')
    elif selected_value == 2:
        Hz = value * 1000000
        return Hz
        #print(value, ' Мегагерц = ', Hz, ' Герц')
    elif selected_value == 3:
        Hz = value * 1000000000
        return Hz
        #print(value, ' Мегагерц = ', Hz, ' Герц')
    elif selected_value == 4:
        return value
        #print ('Конвертация не нужна, введенное значение уже в Герцах')

#проверка ошибок
def error_checker(connect):
    error_check = connect.query(f'SYST:ERR?')
    if '0, No error' not in error_check:
        print(error_check)


def single_stroke(connect):
	connect.write(f'TRIG:SOUR BUS')
	error_checker(CMT)
	connect.write(f'INIT:CONT OFF')
	error_checker(CMT)
	connect.write(f'INIT')
	error_checker(CMT)
	connect.write(f'TRIG:SING')
	error_checker(CMT)
	connect.query(f'*OPC?')

##############################################

CMT.write(f'SYST:PRES')
CMT.write(f'CALC1:PAR:COUN 1')

# параметры для конвертации
# 1.kHz
# 2.MHz
# 3.GHz
# 4.Hz

# устанавливаем точки начала и конца росчерков, 1 и 6 ГГц соответсвенно
CMT.write(f'SENS:FREQ:STAR {hz_converter(1, 3)}')
error_checker(CMT)
CMT.write(f'SENS:FREQ:STOP {hz_converter(6, 3)}')
error_checker(CMT)
#value = int(input('Укажите частоту начала росчерка - '))
#selected_value = int(input('Это: \n 1.kHz \n 2.MHz \n 3.GHz \n 4.Hz \n Введите номер: '))
#CMT.write(f'SENS:FREQ:STAR {hz_converter(value, selected_value)}')

#value = int(input('Укажите частоту конца росчерка - '))
#selected_value = int(input('Это: \n 1.kHz \n 2.MHz \n 3.GHz \n 4.Hz \n Введите номер: '))
#CMT.write(f'SENS:FREQ:STOP {hz_converter(value, selected_value)}')

# устанавливаем 1001 точку в канале
CMT.write(f'SENS:SWE:POIN 1001')
error_checker(CMT)
#points = int(input('Укажите кол-во точек измерения в канале - '))
#CMT.write(f'SENS:SWE:POIN {points}')

# устанавливаем фильтр ПЧ 3 kHz
CMT.write(f'SENS:BWID {hz_converter(3, 1)}')
error_checker(CMT)
#value = int(input('Укажите значение полосы фильтра ПЧ - '))
#selected_value = int(input('Это: \n 1.kHz \n 2.MHz \n 3.GHz \n 4.Hz \n Введите номер: '))
#CMT.write(f'SENS:BWID {hz_converter(value, selected_value)}')

#print('сейчас начнется сбор данных...')
time.sleep(5)

# сбор данных
start_inf = CMT.query(f'SENS:FREQ:STAR?')
error_checker(CMT)
stop_inf = CMT.query(f'SENS:FREQ:STOP?')
error_checker(CMT)
points_inf = CMT.query(f'SENS:SWE:POIN?')
error_checker(CMT)
IF_bandtwith_inf = CMT.query(f'SENS:BWID?')
error_checker(CMT)

print('Канал №1 \n start = ', start_inf, ' Hz \n stop = ', stop_inf, ' Hz \n amount of points = ', points_inf, '\n filter band value = ', IF_bandtwith_inf, ' Hz')

#################################################
#добавляем 4 маркера и устанавливаем их значения
for i in range(1,5):
    CMT.write(f'CALC:MARK{i}:ACT')
    CMT.write(f'CALC:MARK{i}:X {hz_converter(i+1, 3)}')
    time.sleep(1) #я поставила задержку, потому что вместо 4 маркеров ставилось только 2

#включаем статистику
CMT.write(f'CALC:MST ON')

#создаем словарь, куда занесем данные из статистики
dictionary = {}

for i in range(1,5):
    if i == 4:
        CMT.write(f'CALC:MST:DOM:STAR {1}')
        CMT.write(f'CALC:MST:DOM:STOP {4}')
    else:
        CMT.write(f'CALC:MST:DOM:STAR {i}')
        CMT.write(f'CALC:MST:DOM:STOP {i+1}')

    start_inf = CMT.query(f'CALC:MST:DOM:STAR?')
    stop_inf = CMT.query(f'CALC:MST:DOM:STOP?')
    mst_inf = CMT.query(f'CALC:MST:DATA?')
    array = mst_inf.split(',')
    #получаем данные мат. стат-ки между каждой парой маркеров и заносим их в словарь
    dictionary.update({f'{start_inf}-{stop_inf}':{f'mean':f'{array[0]}',f's.dev':f'{array[1]}',f'p-p':f'{array[2]}'}})

for key, value in dictionary.items():
	print(f'Маркеры {key}\n Среднее значение = {value["mean"]} dB \n Стандартное отклонение = {value["s.dev"]} dB \n Фактор пик-пик = {value["p-p"]} dB ')

#делаем пресет
CMT.write(f'SYST:PRES')

#устанавливаем трассу s21
CMT.write(f'CALC:PAR:DEF S21')

#переводим триггер в режим BUS
CMT.write(f'TRIG:SOUR BUS')
error_checker(CMT)

#включаем мат. стат-ку
CMT.write(f'CALC:MST ON')

#функция однократного росчерка
single_stroke(CMT)
error_checker(CMT)

#выводим значение mean
mean = CMT.query(f'CALC:TRAC:MST:DATA?')
array = mean.split(',')
error_checker(CMT)
print(f'mean = {array[0]}')

#включаем усреднение
CMT.write(f'SENS:AVER ON')
error_checker(CMT)

#устанавливаем фактор усреднения 100
aver_factor = 100
CMT.write(f'SENS:AVER:COUN {aver_factor}')
time.sleep(1)

#выполняем рочерк 100 раз
for i in range(int(aver_factor)):
	single_stroke(CMT)

mean = CMT.query(f'CALC:TRAC1:MST:DATA?')
array = mean.split(',')
print(f'mean = {array[0]}')