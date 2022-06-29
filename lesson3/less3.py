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
q = 0.2                                                                                                             #время задержки в секундах, чтобы успеть увидеть действие комнад
CMT.write(f'SYST:PRES')
#Добавляем трассу в канал.
CMT.write(f'CALC1:PAR:COUN 2')
time.sleep(q)

#Изменяем параметр трассы S11 на S22
CMT.write(f'CALC:PAR2:DEF S22')
time.sleep(q)

#Добавляем два маркера на трассу
CMT.write(f'CALC:MARK1:ACT')
CMT.write(f'CALC:MARK2:ACT')
time.sleep(q)

#один из них установим на частоту 3Ghz другой на частоту 3.5Ghz
CMT.write(f'CALC:MARK1:X 3000000000') #3 Ghz
CMT.write(f'CALC:MARK2:X 3500000000') #3,5 Ghz
time.sleep(q)

#Удаляем маркер
marker_check = CMT.query('CALC:MARK?')
if marker_check: CMT.write(f'CALC:MARK OFF')
time.sleep(q)


CMT.write(f'CALC1:PAR:COUN 1') # удляем график (точнее устанавливаем количество графиков, сейчас устаовлен 1 график)
#это были некоторые команды из lesson 2
#теперь lesson 3

CMT.write(f'SYST:PRES')                                                         #сбрасываем настройки до начальных

                                                                                                                     
CMT.write(f'CALC:PAR:COUN 16')                                                       # Добавить 16 трасс в канал
trace_count = int(CMT.query('CALC:PAR:COUN?'))                 #делаем запрос о количестве трасс
print('Количество графиков: ', trace_count)                          #вывод сообщения 

                                                                                                       #Привести трассы к виду 1 трасса s11, 2 трасса s22...16 трасса s1616
count = 1                                                                                    #устанваливаем счетчик на 1, будем сравнивать его с количеством трасс
while count <= trace_count:                                         #цикл до тех пор пока счетчик не совпадет с количеством трасс
    CMT.write(f'CALC:PAR{count}:DEF S{count}{count}')
    count += 1



for i in range(1, trace_count+1, 1):                     #На каждую трассу добавить 2 маркера 1Ghz и 5.5 Ghz                                                                                                   
    CMT.write(f'CALC:PAR{i}:SEL')                           #выбираем активную трассу
    time.sleep(q)
    CMT.write(f'CALC:MARK1:ACT')                             #ставим маркеры
    CMT.write(f'CALC:MARK2:ACT')
    time.sleep(q)
    CMT.write(f'CALC:MARK1:X 1000000000')        #задаем значения 1Ghz и  5.5 Ghz
    CMT.write(f'CALC:MARK2:X 5500000000') 
    time.sleep(q)



for i in range(2, trace_count+1, 2):                        #Каждую четную трассу приветси к виду S номер трассы (номер трассы-1)
                                                                                                         #начинаем со 2й трассы, всего 16(+1 чтобы посчитал последнюю), шаг 2
    CMT.write(f'CALC:PAR{i}:DEF S{i}1')



for i in range(1, trace_count+1, 1):                                                      #вывести в консоль все трассы
    trace_parameter = CMT.query(f'CALC:PAR{i}:DEF?')                # в trace_parameter записываем значение получаемое из запроса CALC:PAR:DEF?
    print('Трасса №', i,' = ', trace_parameter)                                 #выводим полученную информацию
    