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
	
#Функция конвертации множителей kGz,MGh,GHz в герцы
def HzConvertor(n,k):
	if k == "kHz":
		return int(n*1e+3)
	elif k == "MHz":
		return int(n*1e+6)
	elif k == "GHz":
		return int(n*1e+9)
	else: return -1


#Функция нахождения ошибок

def decor(func):
	def CheckError(comand,connect):
		print("start")
		func(comand,connect)
		error_data = connect.query(f'SYST:ERR?')
		if error_data != '0, No error':
			print(error_data)
		print("end")
	return CheckError
		

	
@decor
def Write(comand,connect):
	connect.write(comand)

Write(f'kekw',CMT)	

#Функция однократного росчерка
def singlescan(connect):
	Write(f'TRIG:SOUR BUS', CMT)
	
singlescan(CMT)
