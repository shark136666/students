# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 09:28:15 2021

@author: kuzma.m
"""

import pyvisa
import time
import json
from connect import SNVNAopen
from connect import write
from connect import query
from connect import query_ascii_values
from connect import HzConvertor
from connect import singlescan

#кол-во портов
c = 3

			

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
	
	tracc_count =  c
	#Создаем ветку словоря с шаблона 
	
	atthenuator["atthenuator"][f'{attenuator}']=atthenuator["atthenuator"]['DB']
	atthenuator["atthenuator"][f'{attenuator}']["IF"][f'{int(ifbw/1000)}'] = atthenuator["atthenuator"]['DB']["IF"]['GZ']
	#переменные для вывода максимумов
	max_sdev_abs = float(0)
	max_sdev_otn = float(0)
	#делаем нормализацию для каждой трассы
	for i in range(1,tracc_count+1):

		write(CMT, f'CALC1:PAR:COUN 3')
		write(CMT, f'CALC1:PAR1:DEF S{i}{i}')
		write(CMT, f'CALC1:PAR2:DEF R{i}')
		write(CMT, f'CALC1:PAR2:SPOR {i}')
		write(CMT, f'CALC1:PAR3:DEF T{i}')
		write(CMT, f'CALC1:PAR3:SPOR {i}')
		singlescan(CMT)
		for k in range(1,4):
			write(CMT,f'CALC:PAR{k}:SEL')
			write(CMT,f'CALC:MATH:MEM')
			write(CMT,f'CALC:MATH:FUNC DIV')
			#time.sleep(1)
		#росчерк трасс
		singlescan(CMT)
		
		for k in range(1,4):
			write(CMT,f'CALC:PAR{k}:SEL')
			write(CMT,f'CALC1:MST ON')
			track_def =  query(CMT,f'CALC1:PAR{k}:DEF?')
			#присвоение данных статистики
			mst_data = query_ascii_values(CMT,f'CALC:MST:DATA?')
			
			# поиск макс в S и ввод данных в словарь
			if k == 1:
				atthenuator["atthenuator"][f'{attenuator}']["IF"][f'{int(ifbw/1000)}']["trace"]["otnosit"][f'{track_def}'] = float('{:.5f}'.format(float(mst_data[1])))
				if max_sdev_otn < float(mst_data[1]) or max_sdev_otn == 0:
					max_sdev_otn = float(mst_data[1])
			# поиск макс в R и T и ввод данных в словарь
			else:
				atthenuator["atthenuator"][f'{attenuator}']["IF"][f'{int(ifbw/1000)}']["trace"]["absolute"][f'{track_def}'] = float('{:.5f}'.format(float(mst_data[1])))
				if max_sdev_abs < float(mst_data[1]) or max_sdev_abs == 0:
					max_sdev_abs = float(mst_data[1])
				
	#присвоение максимумов
	atthenuator["atthenuator"][f'{attenuator}']["IF"][f'{int(ifbw/1000)}']["trace"]["absolute"]['max_value'] = float('{:.5f}'.format(max_sdev_abs))
	atthenuator["atthenuator"][f'{attenuator}']["IF"][f'{int(ifbw/1000)}']["trace"]["otnosit"]['max_value'] = float('{:.5f}'.format(max_sdev_otn))

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


	
""" выполнение (; 0_0 0_Q ZVO"""				
algoritm(10,HzConvertor(300,"kHz"))
algoritm(10,HzConvertor(3,"kHz"))
algoritm(30,HzConvertor(300,"kHz"))
algoritm(30,HzConvertor(3,"kHz"))
algoritm(50,HzConvertor(300,"kHz"))
algoritm(50,HzConvertor(3,"kHz"))

#удаление шаблона
for keys in atthenuator["atthenuator"].keys():
	if 'GZ' in atthenuator["atthenuator"][f'{keys}']["IF"].keys():
		del atthenuator["atthenuator"][f'{keys}']["IF"]['GZ']
del atthenuator["atthenuator"]['DB']

#запись в json
with open("sko_result.json", "w") as write_file:
	json.dump(atthenuator, write_file, indent=2)