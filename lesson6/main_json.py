import time
import pyvisa
import json
import configparser
from connect import SNVNAopen, write, query, query_ascii_values, HzConvertor, singlescan

#словарь для хранения входных данных
conf_data = {
	'IFBW':None,
	'range_value':{
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
	for key in config['range_value'].keys():
		conf_data['range_value'][f'{key}'] = HzConvertor(int(config['range_value'][f'{key}']),"kHz")

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
	for range_numb in range(1,int(len(conf_data['range_value'].keys())/2)+1) :
			start = conf_data["range_value"][f'{range_numb}_start']
			stop = conf_data["range_value"][f'{range_numb}_stop']
			jsondict.update({f'{start}-{stop}': {}})
			jsondict[f'{start}-{stop}'].update({'absolute' : {}, 'otnosit' : {}})
			for i in range(1,tracc_count+1):
				write(CMT, f'CALC1:PAR:COUN 3')
				write(CMT, f'CALC1:PAR1:DEF S{i}{i}')
				write(CMT, f'CALC1:PAR2:DEF R{i}')
				write(CMT, f'CALC1:PAR2:SPOR {i}')
				write(CMT, f'CALC1:PAR3:DEF T{i}')
				write(CMT, f'CALC1:PAR3:SPOR {i}')
				
				singlescan(CMT)
				
				
				
			#count = 1
				for trace in range(1,4):
					write(CMT, f'CALC1:PAR{trace}:SEL')
					write(CMT, f'CALC1:TRAC{trace}:MARK1:STAT ON')
					write(CMT, f'CALC1:TRAC{trace}:MARK2:STAT ON')
					write(CMT, f'CALC1:MST ON')
					write(CMT, f'CALC1:MST:DOM ON')
					def_data = query(CMT, f'CALC1:PAR{trace}:DEF?')
					write(CMT, f'CALC1:MARK1:X {start}')
					write(CMT, f'CALC1:MARK2:X {stop}')
					mst_data = query_ascii_values(CMT,f'CALC:MST:DATA?')
					
					if "S" in def_data:
						jsondict[f'{start}-{stop}']['otnosit'].update({f'{def_data}' : mst_data[2]})
					else:
						jsondict[f'{start}-{stop}']['absolute'].update({f'{def_data}' : mst_data[2]})

	
readconfig()
start_frequency_test(conf_data)
with open("p-p_result.json", "w") as write_file:
	json.dump(jsondict, write_file, indent=2)