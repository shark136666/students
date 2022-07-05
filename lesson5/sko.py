# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 09:28:15 2021

@author: kuzma.m
"""

import pyvisa
import time
import json
from connect import SNVNAopen

#функция декоратор
def command_wrapper(f):
    def wrapped(inst, command):
        # print('До функции')
        try:
            if key == "debug":
                print(command)
        except:
            pass
        response = f(inst, command)
        # print('После функции')
        error = inst.query('SYST:ERR?')
        if error != '0, No error':
            print(error)
        return response

    # print('декорируем', f)
    return wrapped

#запрос данных
@command_wrapper
def query(inst, command):
    result = inst.query(command)
    return result

#запрос данных
@command_wrapper
def write(inst, command):
    inst.write(command)

#Функция конвертации множителей kGz,MGh,GHz в герцы
def HzConvertor(n,k):
	if k == "kHz":
		return int(n*1e+3)
	elif k == "MHz":
		return int(n*1e+6)
	elif k == "GHz":
		return int(n*1e+9)
	else: return -1

#Функция однократного росчерка	
def singlescan(connect):
	write(CMT, f'TRIG:SOUR BUS')
	write(CMT, f'INIT:CONT OFF')
	write(CMT, f'INIT')
	write(CMT, f'TRIG:SING')
	query(CMT, f'*OPC?')

#функция добовления трасс
def addtrace(trac):
	#добовляем 'trac' трасс
	write(CMT, f'CALC1:PAR:COUN {trac}')

	#Выставлем трассы T11, R11, S11, T22, R22, S22...
	c = 1
	for i in range(1,trac + 1):
			if (i % 3 == 0):
				write(CMT, f'CALC1:PAR{i}:DEF S{c}{c}')
				c = c + 1
			elif((i + 1) % 3 == 0):
				write(CMT, f'CALC1:PAR{i}:DEF R{c}')
				write(CMT, f'CALC1:PAR{i}:SPOR {c}')
			else:
				write(CMT, f'CALC1:PAR{i}:DEF T{c}')
				write(CMT, f'CALC1:PAR{i}:SPOR {c}')
			

#алгоритм вычеслений СКО
def algoritm(attenuator,ifbw):
	

	#Установить фильтр ПЧ 300 кГц
	write(CMT, f'SENS:BWID {ifbw}')
	time.sleep(1) 

	#Частотный план 
	write(CMT, f'SERV:SWE:FREQ:FACT')

	#Attenuator control – вкл. 
	write(CMT, f'SERV:RFCTL:POW:STAT 1')
	write(CMT, f'SERV:RFCTL:POW:ATT {attenuator}')	

	#установить Код ЦАП.  АЧХ
	write(CMT, f'SERV:RFCTL:POW:DAC 6554')

	#росчерк трасс
	singlescan(CMT)
	
	# вывод статистики
	write(CMT,f'CALC1:MST ON')
	write(CMT,f'CALC1:MST:DOM ON')
	
	tracc_count =  int(query(CMT, f'CALC1:PAR:COUN?'))
	
	#делаем нормализацию для каждой трассы
	for i in range(1,tracc_count+1):

		write(CMT,f'CALC:PAR{i}:SEL')
		write(CMT,f'CALC:MATH:MEM')
		write(CMT,f'CALC:MATH:FUNC DIV')
	
	#росчерк трасс
	singlescan(CMT)
	
	#Создаем ветку словоря с шаблона 
	atthenuator["atthenuator"][f'{attenuator}']=atthenuator["atthenuator"]['DB']
	atthenuator["atthenuator"][f'{attenuator}']["IF"][f'{int(ifbw/1000)}'] = atthenuator["atthenuator"]['DB']["IF"]['GZ']
	
	#переменные для вывода максимумов
	max_sdev_abs = float(0)
	max_sdev_otn = float(0)
	
	for i in range(1,tracc_count+1):
		#вывод статистики 
		write(CMT,f'CALC:PAR{i}:SEL')
		write(CMT,f'CALC1:MST ON')
		write(CMT,f'CALC1:MST:DOM ON')
		track_def =  query(CMT,f'CALC1:PAR{i}:DEF?') 
		
		#присвоение данных статистики
		mst_data = query(CMT,f'CALC:MST:DATA?')
		array = mst_data.split(',')
		
		# поиск макс в S и ввод данных в словарь
		if i % 3 == 0:
			atthenuator["atthenuator"][f'{attenuator}']["IF"][f'{int(ifbw/1000)}']["trace"]["otnosit"][f'{track_def}'] = float(array[1])
			if max_sdev_otn < float(array[1]) or max_sdev_otn == 0:
				max_sdev_otn = float(array[1])
		# поиск макс в R и T и ввод данных в словарь
		else:
			atthenuator["atthenuator"][f'{attenuator}']["IF"][f'{int(ifbw/1000)}']["trace"]["absolute"][f'{track_def}'] = float(array[1])
			if max_sdev_abs < float(array[1]) or max_sdev_abs == 0:
				max_sdev_abs = float(array[1])
				
	#присвоение максимумов
	atthenuator["atthenuator"][f'{attenuator}']["IF"][f'{int(ifbw/1000)}']["trace"]["absolute"]['max_value'] = max_sdev_abs
	atthenuator["atthenuator"][f'{attenuator}']["IF"][f'{int(ifbw/1000)}']["trace"]["otnosit"]['max_value'] = max_sdev_otn

#Словарь для вывода в json файл(шаблон)
atthenuator = {"atthenuator": {
      "DB":{
        "IF":{
          "GZ":{
            "trace":{
              "absolute":{
                "max_value":"value"
              },
              "otnosit":{             
                "max_value":"value"
              }                         
            }
          },
        }
	}
}}
#Подключаемся к SNVNA
CMT = SNVNAopen()

#Пресет
write(CMT, f'SYST:PRES')

#создаем трассы
addtrace(16)
	
""" выполнение (; 0_0 0_Q ZVO"""				
algoritm(10,HzConvertor(300,"kHz"))
algoritm(10,HzConvertor(30,"kHz"))
algoritm(30,HzConvertor(300,"kHz"))
algoritm(30,HzConvertor(30,"kHz"))
algoritm(50,HzConvertor(300,"kHz"))
algoritm(50,HzConvertor(30,"kHz"))

#удаление шаблона
for keys in atthenuator["atthenuator"].keys():
	if 'GZ' in atthenuator["atthenuator"][f'{keys}']["IF"].keys():
		del atthenuator["atthenuator"][f'{keys}']["IF"]['GZ']
del atthenuator["atthenuator"]['DB']

#запись в json
with open("sko_result.json", "w") as write_file:
	json.dump(atthenuator, write_file, indent=2)