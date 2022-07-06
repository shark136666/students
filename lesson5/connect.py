# -*- coding: utf-8 -*-
"""
Created on Mon Jun 21 09:28:15 2021

@author: kuzma.m
"""

import pyvisa as visa

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
	write(connect, f'TRIG:SOUR BUS')
	write(connect, f'INIT:CONT OFF')
	write(connect, f'INIT')
	write(connect, f'TRIG:SING')
	query(connect, f'*OPC?')

def SNVNAopen():	
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
	return CMT

	
	



