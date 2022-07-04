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
	
#Словарь для вывода в json файл
jsondic = {}	

#Подключаемся к SNVNA
CMT = SNVNAopen()

#Пресет
write(CMT, f'SYST:PRES')

def algoritm(trac,attenuator,ifbw):
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


	singlescan(CMT)
	write(CMT,f'CALC1:MST ON')
	write(CMT,f'CALC1:MST:DOM ON')
	
	for i in range(1,trac+1):
		write(CMT,f'CALC:PAR{i}:SEL')
		write(CMT,f'CALC:MATH:MEM')
		write(CMT,f'CALC:MATH:FUNC DIV')

algoritm(7,10,HzConvertor(300,"kHz"))

#with open("sko_result.json", "w") as write_file:
#	json.dump(jsondic, write_file, indent=2)