import time
import pyvisa
import configparser
import json
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
                qwe=[]
                qwe =  config['range'][f'{key}'].split(' ')
                conf_data['range'][f'{key}'] = HzConvertor(int (qwe[0]),qwe[1])

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
        """ ввод колличества потоков """
        tracc_count = 16
        if int(query(CMT,f'SERV:PORT:COUN?')) < tracc_count:
                tracc_count = int(query(CMT,f'SERV:PORT:COUN?'))
        
        param(conf_data)
        double_point()
        config = configparser.ConfigParser()
        config.read_file(open(r'config.txt'))
        #цикл прохождения по диапозонам
        for keys in range(1,int(len(conf_data['range'].keys())/2)+1): 
                start = conf_data["range"][f'{keys}_start']
                stop = conf_data["range"][f'{keys}_stop']
                start_data = config["range"][f'{keys}_start']
                stop_data = config["range"][f'{keys}_stop']
                jsondict.update({f'{start_data} - {stop_data}' : {}})
                jsondict[f'{start_data} - {stop_data}'].update({'absolute' : {},'otnosit' : {}})
                max_p_p_otn = 0
                max_p_p_abs = 0

                for canal in range(1,tracc_count+1):
                    #создание 3 трасс
                    write(CMT, f'CALC1:PAR:COUN 3')
                    write(CMT, f'CALC1:PAR1:DEF S{canal}{canal}')
                    write(CMT, f'CALC1:PAR2:DEF R{canal}')
                    write(CMT, f'CALC1:PAR2:SPOR {canal}')
                    write(CMT, f'CALC1:PAR3:DEF T{canal}')
                    write(CMT, f'CALC1:PAR3:SPOR {canal}')
                    singlescan(CMT)
                    #--------------------
                                
                    for n_trace  in range(1,4):
                        write(CMT, f'CALC:PAR{n_trace}:SEL')
                        write(CMT, f'CALC1:TRAC{n_trace}:MARK1:STAT ON')
                        write(CMT, f'CALC1:TRAC{n_trace}:MARK2:STAT ON')
                        write(CMT, f'CALC1:MARK1:X {start}')
                        write(CMT, f'CALC1:MARK2:X {stop}')
                        write(CMT, f'CALC1:MST ON')
                        write(CMT, f'CALC1:MST:DOM ON')
                        

                        mst_data = query_ascii_values(CMT,f'CALC:MST:DATA?')
                        trace = query(CMT, f'CALC1:PAR{n_trace}:DEF?')
                        if  "S" in trace:
                                jsondict[f'{start_data} - {stop_data}']["otnosit"].update({f'{trace}': mst_data[2] })
                                if max_p_p_otn < float(mst_data[2]) or max_p_p_otn == 0:
                                        max_p_p_otn = float(mst_data[2])
                                        print(max_p_p_otn)
                        else:
                                jsondict[f'{start_data} - {stop_data}']["absolute"].update({f'{trace}': mst_data[2] })
                                if max_p_p_abs < float(mst_data[2]) or max_p_p_abs == 0:
                                        max_p_p_abs = float(mst_data[2])
                                        print(max_p_p_abs)
                jsondict[f'{start_data} - {stop_data}']["otnosit"].update({'max_value': max_p_p_otn})
                jsondict[f'{start_data} - {stop_data}']["absolute"].update({'max_value': max_p_p_abs})
        print(jsondict)
        
	
readconfig()
start_frequency_test(conf_data)
with open("p-p_result.json", "w") as write_file:
	json.dump(jsondict, write_file, indent=2)
