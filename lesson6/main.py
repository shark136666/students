import time
import pyvisa
import configparser
from connect import SNVNAopen, write, query, query_ascii_values, HzConvertor, singlescan

#словарь для хранения входных данных
conf_data = {
	'IFBW':None,
	'range':{
	}
}
#словарь для записи в json
jsondict = {}

CMT = SNVNAopen()

#Функция чтения файла config.txt и записи его значений
def readconfig():
	#Читаем значения из конфиг файла
	config = configparser.ConfigParser()
	config.read_file(open(r'config.txt'))
	
	#Записываем в словарь
	conf_data['IFBW'] = int(config['IFBW']['IFBW'])
	for key in config['range'].keys():
		conf_data['range'][f'{key}'] = HzConvertor(int(config['range'][f'{key}']),"kHz")

def param(conf_data):
	#Пресет
	write(CMT, f'SYST:PRES')
	
	#Attenuator control – вкл. 
	write(CMT, f'SERV:RFCTL:POW:STAT 1')
	write(CMT, f'SERV:RFCTL:POW:ATT 10')	
	
	#Установить фильтр ПЧ из conf_data
	write(CMT, f'SENS:BWID {conf_data["IFBW"]}')
	time.sleep(1) 
	
	#установить Код ЦАП.
	write(CMT, f'SERV:RFCTL:POW:DAC 6554')
	
	#Устанавливаем определенный сегментный план и считываем данные
	write(CMT, f'SERV:SWE:FREQ:FACT')
	

def double_point():
	segm_data = query_ascii_values(CMT,f'SENS:SEGM:DATA?')
	str = 'SENS:SEGM:DATA '
	k = 9
	for i in range(len(segm_data)):
		if i == k:
			segm_data[i] = int(segm_data[i]) * 2
			k += 6
		if i != len(segm_data)-1:
			str += f'{segm_data[i]},'
		else:
			str += f'{segm_data[i]}'
	write(CMT, str)

#Функция проведения тестов и записи в json
def start_frequency_test(conf_data):
	#Подключаемся к SNVNA

	param(conf_data)
	double_point()
	
	tracc_count = 16
	if int(query(CMT,f'SERV:PORT:COUN?')) < tracc_count:
		tracc_count = int(query(CMT,f'SERV:PORT:COUN?'))
	for i in range(1,tracc_count+1):
		write(CMT, f'CALC1:PAR:COUN 3')
		write(CMT, f'CALC1:PAR1:DEF S{i}{i}')
		write(CMT, f'CALC1:PAR2:DEF R{i}')
		write(CMT, f'CALC1:PAR2:SPOR {i}')
		write(CMT, f'CALC1:PAR3:DEF T{i}')
		write(CMT, f'CALC1:PAR3:SPOR {i}')
		
		singlescan(CMT)
		
		write(CMT, f'CALC1:TRAC1:MARK1:STAT ON')
		write(CMT, f'CALC1:TRAC1:MARK2:STAT ON')
		
		write(CMT, f'CALC1:MST ON')
		write(CMT, f'CALC1:MST:DOM ON')
		
		count = 1
		for keys in conf_data['range'].keys():
			if count %2 = 1:
				write(CMT, f'CALC1:MARK1:X {conf_data["range"]["{keys}"]}')
			else:
				write(CMT, f'CALC1:MARK2:X {conf_data["range"]["{keys}"]}')
				mst_data = query_ascii_values(CMT,f'CALC:MST:DATA?')
			count+=1
	

	
	
readconfig()
start_frequency_test(conf_data)